# Required packages
library(httr)
library(jsonlite)
library(stringr)
library(readr)

# ---------------------- User Settings ----------------------
input_json_path <- "filtered_by_topics.json"    # Input data (messages) in JSON format
codes_txt_path <- "codes_with_desc_RU.txt"      # File with codes/descriptions (in Russian)
output_folder <- "GPT_outputs"                  # Output directory for results

batch_size <- 5      # Number of messages per GPT batch
sleep_seconds <- 1   # Pause between requests

process_from <- 1    # Starting row (1-based)
process_to <- NA     # Ending row (NA = till end of file)

openai_api_key <- "YOUR_API_KEY_HERE"      # Your OpenAI API key
openai_model <- "gpt-4.1"                  # Model name ("gpt-4o" also possible)

log_file <- file.path(output_folder, "processing_log.txt")   # Log file path

# ---------------------- Helper Functions ----------------------
log_msg <- function(msg) {
  timestamp <- format(Sys.time(), "%Y-%m-%d %H:%M:%S")
  line <- paste0("[", timestamp, "] ", msg)
  cat(line, "\n")
  cat(line, "\n", file=log_file, append=TRUE)
}

read_codes <- function(path) {
  lines <- read_lines(path)
  codes <- list()
  for (line in lines) {
    if (str_trim(line) == "" || str_starts(line, "#")) next
    parts <- str_split_fixed(line, "\t", 2)
    code_num <- str_trim(parts[1])
    desc <- str_trim(parts[2])
    codes[[code_num]] <- desc
  }
  return(codes)
}

build_prompt <- function(messages_df, codes) {
  codes_text <- paste0(
    paste0(names(codes), ": ", unlist(codes)),
    collapse = "\n"
  )
  messages_text <- paste0(
    apply(messages_df, 1, function(row) {
      paste0("ID ", row["global_id"], ":\n", row["text"])
    }),
    collapse = "\n\n---\n\n"
  )
  prompt <- paste0(
    "You are a professional academic researcher and expert in thematic content analysis of texts.\n",
    "Your task is to analyze each of the following texts separately (texts are separated by '---').\n",
    "For each text, determine:\n",
    " 1) Which codes from the provided list are present (max 5 codes per text; codes are specified by number).\n",
    " 2) Whether the text contains explicit opinion or commentary by the author (respond 0 = no opinion, 1 = opinion present).\n",
    "If the text does not fit any theme, use code '99'. If you think new themes should be added, suggest them separately.\n",
    "Output strictly in JSON format — an array of objects: 'id' (message number), 'Codes' (array), 'Opinion' (0 or 1).\n",
    "Example: [{\"id\": 12, \"Codes\": [3, 10], \"Opinion\": 1}, {\"id\": 13, \"Codes\": [99], \"Opinion\": 0}]\n\n",
    "List of codes:\n", codes_text, "\n\n",
    "Messages to analyze:\n\n", messages_text, "\n\n",
    "Reply only with JSON, no comments or explanations."
  )
  return(prompt) # Originally, the prompt was written in Russian. This is a translation.
}

parse_response <- function(raw_reply) {
  # Extract JSON array from the response text
  json_start <- str_locate(raw_reply, "\\[")[1]
  json_end <- tail(str_locate_all(raw_reply, "\\]")[[1]][,2], 1)
  json_text <- substr(raw_reply, json_start, json_end)
  parsed <- fromJSON(json_text, simplifyDataFrame = TRUE)
  return(parsed)
}

call_openai_api <- function(prompt, model, api_key) {
  url <- "https://api.openai.com/v1/chat/completions"
  body <- list(
    model = model,
    messages = list(list(role = "user", content = prompt)),
    temperature = 0
  )
  headers <- add_headers(
    Authorization = paste("Bearer", api_key),
    `Content-Type` = "application/json"
  )
  for (attempt in 1:3) {
    tryCatch({
      response <- POST(url, headers, body = toJSON(body, auto_unbox = TRUE), timeout(60))
      if (status_code(response) != 200) {
        log_msg(paste0("OpenAI API error (status ", status_code(response), "), attempt ", attempt))
        Sys.sleep(3)
        next
      }
      res_text <- content(response, as = "text", encoding = "UTF-8")
      res_json <- fromJSON(res_text, simplifyDataFrame = FALSE)
      return(res_json$choices[[1]]$message$content)
    }, error = function(e) {
      log_msg(paste0("OpenAI API call error: ", e$message, ", attempt ", attempt))
      Sys.sleep(3)
    })
  }
  stop("Failed to get response from OpenAI API after 3 attempts.")
}

get_batches <- function(df, batch_size) {
  n <- nrow(df)
  split(df, ceiling(seq_len(n) / batch_size))
}

# ---------------------- Main Script ----------------------
dir.create(output_folder, showWarnings = FALSE)
log_msg("=== Processing started ===")

codes <- read_codes(codes_txt_path)
log_msg(paste0("Codes loaded: ", length(codes)))

all_data <- fromJSON(input_json_path)
n_total <- nrow(all_data)
log_msg(paste0("Total messages: ", n_total))

if (is.na(process_to)) process_to <- n_total
if (process_from < 1 || process_to > n_total || process_from > process_to) stop("Invalid processing range.")

selected_data <- all_data[process_from:process_to, ]
selected_data$global_id <- seq(from = process_from, length.out = nrow(selected_data))

batches <- get_batches(selected_data, batch_size)
n_batches <- length(batches)
log_msg(paste0("Total batches: ", n_batches))

results <- selected_data
results$Codes <- NA
results$Opinion <- NA

total_words_sent <- 0

for (bi in seq_len(n_batches)) {
  batch_df <- batches[[bi]]
  log_msg(sprintf("Processing batch %d of %d (messages %d-%d)",
                  bi, n_batches, min(batch_df$global_id), max(batch_df$global_id)))
  
  prompt <- build_prompt(batch_df, codes)
  n_words_batch <- sum(str_count(batch_df$text, boundary("word")))
  total_words_sent <- total_words_sent + n_words_batch
  log_msg(sprintf("Words sent in this batch: %d (cumulative: %d)", n_words_batch, total_words_sent))
  
  response_text <- call_openai_api(prompt, openai_model, openai_api_key)
  
  parsed <- tryCatch({
    parse_response(response_text)
  }, error = function(e) {
    log_msg(paste0("Parsing error in batch ", bi, ": ", e$message))
    NULL
  })
  if (is.null(parsed)) {
    log_msg(sprintf("Skipping batch %d due to parsing error", bi))
    next
  }
  
  for (ri in seq_len(nrow(parsed))) {
    res <- parsed[ri, ]
    idx <- which(results$global_id == res$id)
    if (length(idx) == 1) {
      codes_str <- if (is.list(res$Codes)) paste(unlist(res$Codes), collapse = ";") else paste(res$Codes, collapse = ";")
      results$Codes[idx] <- codes_str
      results$Opinion[idx] <- res$Opinion
    }
  }
  codes_found <- unique(unlist(parsed$Codes))
  log_msg(sprintf("Batch %d: processed %d messages, codes: %s", bi, nrow(batch_df), paste(codes_found, collapse = ",")))
  Sys.sleep(sleep_seconds)
}

output_json_path <- file.path(output_folder, sprintf("output_%d_to_%d.json", process_from, process_to))
output_csv_path  <- file.path(output_folder, sprintf("output_%d_to_%d.csv", process_from, process_to))

write_json(results, output_json_path, pretty = TRUE, auto_unbox = TRUE)
write.csv(results, output_csv_path, row.names = FALSE)

log_msg(sprintf("=== Processing complete. Results saved in %s ===", output_folder))
log_msg(sprintf("Total words sent to GPT: %d", total_words_sent))

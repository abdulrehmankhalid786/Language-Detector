import re
import os


def remove_special_characters(input_string):
    # Using regular expression to remove special characters
    cleaned_string = re.sub(r'[^a-zA-Z\\s]+', ' ', input_string)
    # Remove leading and trailing spaces
    cleaned_string = cleaned_string.strip()
    return cleaned_string


def generate_ngrams(word):
    word_padded = '_' + word.replace(' ', '_') + '_'
    length = len(word_padded)

    uni_grams = list(word.replace(' ', ''))
    bi_grams = [''.join(word_padded[i:i+2]) for i in range(length - 1)]
    tri_grams = [''.join(word_padded[i:i+3]) + '_'*(3-(length-i))
                 for i in range(length - 1)]
    quad_grams = [''.join(word_padded[i:i+4]) + '_'*(4-(length-i))
                  for i in range(length - 1)]

    return uni_grams, bi_grams, tri_grams, quad_grams


def calculate_ngram_frequency(ngrams_list):
    ngram_freq = {}
    for ngram in ngrams_list:
        ngram_freq[ngram] = ngram_freq.get(ngram, 0) + 1
    return ngram_freq


def sorted_ngram_frequency(text):
    cleaned_string = remove_special_characters(text)

    uni_grams, bi_grams, tri_grams, quad_grams = generate_ngrams(
        cleaned_string.lower())
    # Calculate n-gram frequencies
    uni_gram_freq = calculate_ngram_frequency(uni_grams)
    bi_gram_freq = calculate_ngram_frequency(bi_grams)
    tri_gram_freq = calculate_ngram_frequency(tri_grams)
    quad_gram_freq = calculate_ngram_frequency(quad_grams)

    # Sort n-gram frequencies in descending order
    sorted_uni_gram_freq = {k: v for k, v in sorted(
        uni_gram_freq.items(), key=lambda item: item[1], reverse=True)}
    sorted_bi_gram_freq = {k: v for k, v in sorted(
        bi_gram_freq.items(), key=lambda item: item[1], reverse=True)}
    sorted_tri_gram_freq = {k: v for k, v in sorted(
        tri_gram_freq.items(), key=lambda item: item[1], reverse=True)}
    sorted_quad_gram_freq = {k: v for k, v in sorted(
        quad_gram_freq.items(), key=lambda item: item[1], reverse=True)}

    sorted_ngram_freq = {'uni_gram': sorted_uni_gram_freq, 'bi_gram': sorted_bi_gram_freq,
                         'tri_gram': sorted_tri_gram_freq, 'quad_gram': sorted_quad_gram_freq}

    return sorted_ngram_freq


def calculate_out_of_place_measure(text_freq, reference_freq):
    """
    Calculate the out-of-place measure between two dictionaries representing n-gram frequencies.

    Parameters:
    - text_freq: Dictionary representing n-gram frequencies of the input text.
    - reference_freq: Dictionary representing n-gram frequencies of the reference language.

    Returns:
    - out_of_place_measure: The calculated out-of-place measure.
    """
    out_of_place_measure = 0

    all_keys = set().union(
        text_freq['uni_gram'], text_freq['bi_gram'], text_freq['tri_gram'], text_freq['quad_gram'])

    for key in all_keys:
        text_position = text_freq['uni_gram'].get(key, 0) + text_freq['bi_gram'].get(key, 0) + \
            text_freq['tri_gram'].get(
                key, 0) + text_freq['quad_gram'].get(key, 0)

        reference_position = reference_freq['uni_gram'].get(key, 0) + reference_freq['bi_gram'].get(key, 0) + \
            reference_freq['tri_gram'].get(
                key, 0) + reference_freq['quad_gram'].get(key, 0)

        out_of_place_measure += abs(text_position - reference_position)

    return out_of_place_measure


def detect_language(input_text, reference_languages):

    input_ngram_freq = sorted_ngram_frequency(input_text)
    # Calculate out-of-place measure for each reference language
    results = {}
    for language, reference_freq in reference_languages.items():
        out_of_place_measure = calculate_out_of_place_measure(
            input_ngram_freq, reference_freq)
        results[language] = out_of_place_measure

    # Determine the language with the minimum out-of-place measure
    detected_language = max(results, key=results.get)

    return detected_language, results


def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found."
    except Exception as e:
        return f"Error: An unexpected error occurred - {str(e)}"
    return content


if __name__ == '__main__':
    dataset = 'language dataset'
    reference_languages = {}
    file_paths = ['English.txt', 'Spanish.txt', 'French.txt', 'German.txt']

    for file_path in file_paths:
        text = process_file(os.path.join(dataset, file_path))
        result = sorted_ngram_frequency(text)
        reference_languages[file_path.split('.')[0]] = result

    input_text = "This is an example sentence in English."
    # input_text = "En la Pintura la parte mas pequeña será la que mas presto se pierda de"
    # input_text = "Dennoch entgeht es wohl dem tiefer Blickenden nicht, daß die Jugend des"
    # input_text = "Tous droits de reproduction, de traduction et d’adaptation réservés pour"

    # Detect language based on out-of-place measure
    detected_language, results = detect_language(
        input_text, reference_languages)

    # Display the results
    print(f"Detected Language: {detected_language}")
    print("Out-of-Place Measure Results:")
    for language, measure in results.items():
        print(f"{language}: {measure}")

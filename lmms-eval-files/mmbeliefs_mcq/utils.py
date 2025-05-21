import datetime
import json
import re
import string

from loguru import logger as eval_logger
import lmms_eval.tasks._task_utils.file_utils as file_utils


def normalize_text(s):
    """
    Normalize a text string for comparison:
    - Lowercase
    - Strip punctuation
    - Collapse whitespace
    """
    s = s.lower()
    s = s.translate(str.maketrans('', '', string.punctuation))
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def extract_choice_letter(response):
    """
    Extract the letter (A-E) from a response like 'C', 'C)', or 'C) Fascist'.

    Returns:
        str: Uppercase letter if valid, else None.
    """
    match = re.match(r"\s*([A-Ea-e])[\):\s]?", response)
    return match.group(1).upper() if match else None


def multiple_choice_accuracy(response, candidate_answers, superset_correct_answers):
    """
    Determine if the model response corresponds to a correct answer via letter-to-answer mapping.

    Args:
        response (str): Model output (e.g., 'C', 'C) Fascist').
        candidate_answers (List[str]): The multiple choice options.
        superset_correct_answers (List[str]): Valid groundtruth answers (e.g., ['Fascist', 'Nazi']).

    Returns:
        float: 1.0 if correct, else 0.0
    """
    letter = extract_choice_letter(response)
    if not letter:
        return 0.0

    index = ord(letter) - ord('A')
    if not (0 <= index < len(candidate_answers)):
        return 0.0

    predicted_answer = candidate_answers[index]
    norm_pred = normalize_text(predicted_answer)
    norm_gts = [normalize_text(gt) for gt in superset_correct_answers]

    return 1.0 if norm_pred in norm_gts else 0.0


def mmbeliefs_doc_to_visual(doc):
    """
    Extract image input for the model.

    Args:
        doc (dict): Input document.

    Returns:
        List[Image]: A list containing a single RGB image.
    """
    return [doc["image"].convert("RGB")]


def mmbeliefs_doc_to_text(doc, lmms_eval_specific_kwargs=None):
    """
    Construct the textual input prompt from the document.

    Args:
        doc (dict): Input document with a 'question' field.
        lmms_eval_specific_kwargs (dict): Optional dict with keys "pre_prompt" and "post_prompt".

    Returns:
        str: Full prompt string.
    """
    pre_prompt = lmms_eval_specific_kwargs.get("pre_prompt", "") if lmms_eval_specific_kwargs else ""
    post_prompt = lmms_eval_specific_kwargs.get("post_prompt", "") if lmms_eval_specific_kwargs else ""
    return f"{pre_prompt}{doc['question']}{post_prompt}"


def mmbeliefs_process_results(doc, result):
    """
    Evaluate a model-generated multiple choice result.

    Args:
        doc (dict): Must include 'candidate_answers' and 'superset_correct_answers'.
        result (List[str]): Model prediction as a list with one string.

    Returns:
        dict: Dictionary with 'exact_match' score and 'submission' answer.
    """
    assert len(result) == 1, f"Expected result to be a list of length 1, got {len(result)}."
    prediction = result[0]

    candidate_answers = doc["candidate_answers"]
    superset_correct_answers = doc["superset_correct_answers"]

    accuracy = multiple_choice_accuracy(prediction, candidate_answers, superset_correct_answers)

    return {
        "exact_match": accuracy,
        "submission": {
            "answer": prediction,
        },
    }


def mmbeliefs_process_results_test(doc, result):
    """
    Format test results for submission.

    Args:
        doc (dict): Input document.
        result (List[str]): Model prediction.

    Returns:
        dict: Submission dictionary.
    """
    res = mmbeliefs_process_results(doc, result)
    return {
        "submission": res["submission"],
    }


def mmbeliefs_process_results_val(doc, result):
    """
    Format validation results for metric evaluation.

    Args:
        doc (dict): Input document.
        result (List[str]): Model prediction.

    Returns:
        dict: Dictionary with 'exact_match' score.
    """
    res = mmbeliefs_process_results(doc, result)
    return {
        "exact_match": res["exact_match"],
    }


def mmbeliefs_aggregate_submissions(results, args):
    """
    Save submission results to file.

    Args:
        results (List[dict]): List of submission dictionaries.
        args (Namespace): Arguments that include output directory.

    Returns:
        None
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"mmbeliefs-test-submission-{now}.json"
    output_path = file_utils.generate_submission_file(filename, args)
    with open(output_path, "w") as f:
        json.dump(results, f)
    eval_logger.info(f"Submission file saved to {output_path}")

import datetime
import json

NEW_ITEM = '\n '


def hash_str(test: str) -> str:
    return


def timestamp_to_date_str(timestamp: float):
    return datetime.datetime.fromtimestamp(timestamp)


def easy_duration_str(start_time, end_time):
    # Calculate the elapsed time in seconds
    elapsed = int(abs(end_time - start_time))

    # Convert seconds into hours, minutes, and seconds
    hours, remainder = divmod(elapsed, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format the output string
    output = f"{hours} hours, {minutes} minutes, and {seconds} seconds"

    # Print the output string
    return output


def easy_command_summary_str(num: int, command: dict):
    duration = easy_duration_str(command.get('start_time'),
                                 command.get('end_time'))
    success = 'success' if command.get('success') else 'not success'
    return f"{num}. Command `{command.get('command')}`" \
           f"\n\tStart time: {timestamp_to_date_str(command.get('start_time'))}" \
           f"\n\tEnd time: {timestamp_to_date_str(command.get('end_time'))}" \
           f"\n\tDuration: {duration}" \
           f"\n\tReturn code: {command.get('return_code')}" \
           f"\n\tStatus: {success}."


def process_file(json_path):
    with open(json_path, "r") as _fh:
        erasure = json.load(_fh)

    markdown_text = """
# Erasure Details

Device:
Serial:
Total duration:

## Steps

Total: 
Summary:
"""

    for step in erasure.get("steps", []):
        dt_start = timestamp_to_date_str(step.get("date_init"))
        dt_end = timestamp_to_date_str(step.get("date_end"))
        markdown_text += f"""
### Step {step.get("step")}

Start: {dt_start}
Finished: {dt_end}
Total duration: {easy_duration_str(step.get("date_end"), step.get("date_init"))}

## Commands

 {NEW_ITEM.join(
            (easy_command_summary_str(num + 1, cmd)
             for num, cmd in enumerate(step.get("commands"))))}

## Validation

Result: {step.get("validation", {}).get("validation")}
"""


if __name__ == '__main__':
    path_to_erasure_json = "2023-06-06_120312E2M3121K00UN6S.json"
    process_file(path_to_erasure_json)

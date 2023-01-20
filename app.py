import pandas as pd
from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

def filter_stocks(input_text, df):
    # Define the keywords and their corresponding column names
    keywords = {
        "low": "LOW",
        "high": "HIGH",
        "close": "CLOSE",
        "open": "OPEN",
        "volume": "VOLUME",
        "previous close": "PCLOSE"
    }

    # Initialize an empty list to store the conditions
    conditions = []

    # Split the input text into a list of words
    words = input_text.split()

    # Iterate over the words in the input text
    for i, word in enumerate(words):
        # Check if the word is a keyword
        if word in keywords:
            # Check if the next word is "is"
            if words[i+1] == "is":
                # Check if the next word is "more" or "less"
                if words[i+2] == "more":
                    operator = ">"
                elif words[i+2] == "less":
                    operator = "<"
                else:
                    raise ValueError("Invalid operator): {}".format(words[i+2]))
                            # Check if the next word is "than"
            if words[i+3] != "than":
                raise ValueError("Expected keyword 'than' after operator")

            # Get the value of the condition
            value = float(words[i+4])

            # Check if the next word is "percent" or "percentage" and if so, multiply the value by 0.01
            if words[i+5] in ["percent", "percentage"]:
                value *= 0.01
            
            above_below = None
            if "above" in words[i+5:i+7]:
                above_below = "above"
            elif "below" in words[i+5:i+7]:
                above_below = "below"
            else:
                above_below = None
            
            if above_below:
                if words[i+6] == "the":
                    if words[i+7] == "previous":
                        if words[i+8] in keywords:
                            if words[i+9] == "is":
                                if above_below == "above":
                                    conditions.append("{} {} {}+{}".format(keywords[word], operator, keywords[words[i+8]], value))
                                else:
                                    conditions.append("{} {} {}-{}".format(keywords[word], operator, keywords[words[i+8]], value))
                            else:
                                raise ValueError("Expected keyword 'is' after {}".format(words[i+8]))
                        else:
                            raise ValueError("Expected keyword 'close', 'open', 'high', 'low' or 'volume' after the")
                    else:
                        raise ValueError("Expected keyword 'previous' after the")
                else:
                    raise ValueError("Expected keyword 'the' after {}".format(words[i+5]))
            
            else:
                conditions.append("{} {} {}".format(keywords[word], operator, value))
        else:
            raise ValueError("Expected keyword 'is' after {}".format(word))

# check if conditions are all met
filtered_df = df.query(" and ".join(conditions))

# Return the filtered DataFrame
return filtered_df
@app.route('/', methods=['GET', 'POST'])
def index():
if request.method == 'POST':
# Get the CSV file and filter input from the form
csv_file = request.files['csv_file']
filter_input = request.form['filter_input']
    # Validate the file extension
    if not csv_file or not re.search(r'([^\s]+(?i)(csv))$', csv_file.filename):
        return jsonify({'error': 'Invalid file format, please upload a CSV file'})
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Filter the DataFrame using the filter_stocks function
    filtered_df = filter_stocks(filter_input, df)

    # Render the template and pass in the filtered DataFrame
    return render_template('index.html', filtered_df=filtered_df)

return render_template('index.html')
if name == 'main':
app.run()

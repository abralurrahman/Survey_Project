
from flask import Flask, render_template, request, redirect, session, url_for
from flask import Response
import csv
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'secret_key'  # Secret key for session management


# Connect to the database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# Middleware to ensure the language is set for each page
@app.before_request
def set_language():
    if 'language' not in session:
        session['language'] = 'en'  # Default language is English


# Function to get random images for choice experiments
def get_random_images(total_images, selected_images):
    available_images = [i for i in range(1, total_images + 1) if i not in selected_images]
    return random.sample(available_images, 2)


# Home route to display the intro page
@app.route('/')
def intro():
    return render_template('intro.html', language=session.get('language'))


# Route to change language
@app.route('/change-language', methods=['POST'])
def change_language():
    language = request.form.get('language')
    session['language'] = language
    return redirect(request.referrer)  # Redirect back to the page the user was on


@app.route('/submit', methods=['POST'])
def submit():
    consent = request.form.get('consent')
    if consent == 'yes':
        # Reset session variables for a new survey
        session['selected_images'] = []
        session['current_page'] = 1
        session['popup_triggered'] = False  # Ensure pop-up can show again
        session.pop('stored_images', None)  # Clear stored images
        return redirect('/choice-experiment')
    else:
        return redirect('/no-consent')


@app.route('/start-survey')
def start_survey():
    session.clear()  # Clear all previous session variables
    session['selected_images'] = []  # List of selected images
    session['popup_triggered'] = False  # Popup has not yet been triggered
    session['popup_shown_set'] = random.randint(1, 3)  # Randomly choose one set for the popup
    session['stored_images'] = None  # Reset stored images
    return redirect('/choice-experiment')  # Redirect to the choice experiment


IMAGES = [
    {"id": 1, "filename": "child_simple.jpg", "description": "Child"},
    {"id": 2, "filename": "Disability.jpg", "description": "Person with Disability"},
    {"id": 3, "filename": "old_male_female_simpler.jpg", "description": "Elderly Couple"},
    {"id": 4, "filename": "Overweight_simpler.jpg", "description": "Overweight Person"},
    {"id": 5, "filename": "test_0_0_1_1_0.jpg", "description": "Test Image 1"},
    {"id": 6, "filename": "test_0_0_2_3_1.jpg", "description": "Test Image 2"},
    {"id": 7, "filename": "test_0_2_3_3_2.jpg", "description": "Test Image 3"},
    {"id": 8, "filename": "test_1_0_3_2_0.jpg", "description": "Test Image 4"},
    {"id": 9, "filename": "test_1_3_2_2_1.jpg", "description": "Test Image 5"},
    {"id": 10, "filename": "Patient_at_Laptop_with_Head_Bandage.png", "description": "Patient at Laptop with Head Bandage"},
    {"id": 11, "filename": "Patient_on_a_Stretcher.png", "description": "Patient on a Stretcher"},
    {"id": 12, "filename": "Patient_with_Arm_Sling.png", "description": "Patient with Arm Sling"},
    {"id": 13, "filename": "Patient_with_IV_and_Arm_Sling.jpg", "description": "Patient with IV and Arm Sling"},
    {"id": 14, "filename": "Patient_with_IV_Drip.png", "description": "Patient with IV Drip"},
    {"id": 15, "filename": "pregnant_woman_care.webp", "description": "Pregnant Woman Care"},
    {"id": 16, "filename": "Pregnant_woman_lying_on_hospital_bed.png", "description": "Pregnant Woman Lying on Hospital Bed"},
    {"id": 17, "filename": "Walking_Patient_with_Crutches.jpg", "description": "Walking Patient with Crutches"}
]


# Update the filename paths to use the resized directory
for image in IMAGES:
    image["filename"] = f"resized_images/{image['filename']}"


@app.route('/choice-experiment', methods=['GET', 'POST'])
def choice_experiment():
    # Initialize session variables if not already set
    if 'selected_images' not in session:
        session['selected_images'] = []
    if 'popup_triggered' not in session:
        session['popup_triggered'] = False
    if 'popup_shown_set' not in session:
        session['popup_shown_set'] = random.randint(1, 3)  # Randomly select one set for popup
    if 'stored_images' not in session:
        session['stored_images'] = None  # Initialize storage for popup images

    if request.method == 'POST':
        selected_image = request.form.get('selected_image')

        # Save the selected image in session
        session['selected_images'].append(selected_image)

        # Handle the popup logic
        current_set_number = len(session['selected_images'])  # Determine the current set number
        if current_set_number == session['popup_shown_set'] and not session['popup_triggered']:
            session['popup_triggered'] = True
            session['stored_images'] = session['current_images']  # Store current images for reconsideration
            session['opposite_image'] = (
                session['current_images'][1]
                if session['current_images'][0] == selected_image
                else session['current_images'][0]
            )
            return redirect('/reconsider')  # Redirect to the reconsideration page

        # Redirect to procedural ratings if this was the last set (3 sets assumed)
        if len(session['selected_images']) >= 3:
            return redirect('/procedural-ratings')

    # Reload the same images if the popup was triggered
    if session['popup_triggered'] and session['stored_images']:
        images = [
            next(img for img in IMAGES if img["filename"] == session['stored_images'][0]),
            next(img for img in IMAGES if img["filename"] == session['stored_images'][1]),
        ]
    else:
        # Select two random images from the available ones
        used_images = set(session.get('selected_images', []))
        available_images = [img for img in IMAGES if img["filename"] not in used_images]

        if len(available_images) < 2:
            return redirect('/procedural-ratings')  # No more images, go to ratings

        images = random.sample(available_images, 2)
        session['current_images'] = [img["filename"] for img in images]  # Store the current pair

    return render_template('choice_experiment.html', images=images, page=len(session['selected_images']) + 1)



@app.route('/reconsider', methods=['GET', 'POST'])
def reconsider():
    if request.method == 'POST':
        # Get the final reconsidered choice
        final_choice = request.form.get('selected_image')

        # Update the last selected image with the reconsidered choice
        session['selected_images'][-1] = final_choice

        # If this is the last set, redirect to ratings
        if len(session['selected_images']) >= 3:
            return redirect('/procedural-ratings')

        # Reset the popup state and redirect back to the choice experiment
        session['popup_triggered'] = False
        return redirect('/choice-experiment')

    # Render the reconsideration page with stored images
    stored_images = session.get('stored_images', [])
    reconsider_image = session.get('opposite_image')
    opposite_image_description = next(
        (img["description"] for img in IMAGES if img["filename"] == reconsider_image),
        "No description available"
    )

    return render_template(
        'reconsider.html',
        reconsider_image=reconsider_image,
        opposite_image_description=opposite_image_description,
        images=[
            next(img for img in IMAGES if img["filename"] == stored_images[0]),
            next(img for img in IMAGES if img["filename"] == stored_images[1]),
        ]
    )

@app.route('/procedural-ratings', methods=['GET', 'POST'])
def procedural_ratings():
    # List of questions with short IDs and full labels
    questions = [
        {"id": "save_life_years", "label": "Save the most life years..."},
        {"id": "advantage_disadvantaged", "label": "Provide advantage to the disadvantaged..."},
        {"id": "benefit_future", "label": "Benefit to others in the future..."},
        {"id": "first_come", "label": "First-come, first-served..."},
        {"id": "treatment_success", "label": "Maximize treatment success..."},
        {"id": "treatment_effort", "label": "Minimize treatment effort..."},
        {"id": "medication_effect", "label": "Maximize the medication effect..."},
        {"id": "random_selection", "label": "Random selection..."},
    ]

    if request.method == 'POST':
        question_id = request.form.get('question_id')
        rating = request.form.get('rating')

        # Store ratings in session
        if 'ratings' not in session:
            session['ratings'] = {}

        session['ratings'][question_id] = rating

        # Save to database when all questions are completed
        if len(session['ratings']) == len(questions):
            conn = get_db_connection()
            conn.execute('''
                UPDATE user_responses
                SET save_life_years = ?, advantage_disadvantaged = ?, benefit_future = ?, first_come = ?,
                    treatment_success = ?, treatment_effort = ?, medication_effect = ?, random_selection = ?
                WHERE id = (SELECT MAX(id) FROM user_responses)
            ''', [
                session['ratings'].get('save_life_years'),
                session['ratings'].get('advantage_disadvantaged'),
                session['ratings'].get('benefit_future'),
                session['ratings'].get('first_come'),
                session['ratings'].get('treatment_success'),
                session['ratings'].get('treatment_effort'),
                session['ratings'].get('medication_effect'),
                session['ratings'].get('random_selection'),
            ])
            conn.commit()
            conn.close()

            session.pop('ratings', None)
            return redirect('/demography')

        # Move to the next question
        current_index = next((i for i, q in enumerate(questions) if q['id'] == question_id), -1) + 1
        if current_index >= len(questions):
            return redirect('/demography')  # Redirect to demography if all questions are answered
        return redirect(f'/procedural-ratings?index={current_index}')

    # Get the current question based on the index in the query parameter
    current_index = int(request.args.get('index', 0))
    if current_index >= len(questions):
        return redirect('/demography')  # Redirect to demography if index exceeds the number of questions
    question = questions[current_index]
    return render_template('procedural_ratings.html', question=question, index=current_index)


@app.route('/demography', methods=['GET', 'POST'])
def demography():
    # List of demographic questions with short IDs and full labels
    questions = [
        {
            "id": "gender",
            "label": "What describes you best?",
            "type": "radio",
            "options": [
                {"value": "female", "label": "Female"},
                {"value": "male", "label": "Male"},
                {"value": "diverse", "label": "Diverse"},
                {"value": "prefer_not_to_disclose", "label": "Prefer not to disclose"}
            ]
        },
        {
            "id": "age",
            "label": "How old are you?",
            "type": "number",
            "placeholder": "Age (in years)"
        },
        {
            "id": "religion",
            "label": "Do you identify yourself with any of the following religions?",
            "type": "radio",
            "options": [
                {"value": "none", "label": "No, I do not"},
                {"value": "christian", "label": "Christian"},
                {"value": "islam", "label": "Islam"},
                {"value": "hinduism", "label": "Hinduism"},
                {"value": "buddhism", "label": "Buddhism"},
                {"value": "other", "label": "Other"}
            ]
        },
    ]

    if request.method == 'POST':
        # Get the current question's ID and user's response
        question_id = request.form.get('question_id')
        answer = request.form.get('answer')

        # Initialize session for demographic answers if not already done
        if 'demography_answers' not in session:
            session['demography_answers'] = {}

        # Store the response using the question's ID
        session['demography_answers'][question_id] = answer

        # Move to the next question
        current_index = next((i for i, q in enumerate(questions) if q['id'] == question_id), -1)
        next_index = current_index + 1

        if next_index >= len(questions):
            # Save all responses to the database
            conn = get_db_connection()
            conn.execute('''
                UPDATE user_responses
                SET gender = ?, age = ?, religion = ?
                WHERE id = (SELECT MAX(id) FROM user_responses)
            ''', [
                session['demography_answers'].get('gender'),
                session['demography_answers'].get('age'),
                session['demography_answers'].get('religion'),
            ])
            conn.commit()
            conn.close()

            # Clear the demographic answers session data
            session.pop('demography_answers', None)
            return redirect('/group-preferences')

        # Redirect to the next question
        return redirect(f'/demography?index={next_index}')

    # Get the current question based on the index in the query parameter
    current_index = int(request.args.get('index', 0))
    question = questions[current_index]
    return render_template('demography.html', question=question, index=current_index)


@app.route('/group-preferences', methods=['GET', 'POST'])
def group_preferences():
    # List of group preference questions with short IDs and full labels
    questions = [
        {
            "id": "general_health",
            "label": "How is your health in general?",
            "type": "select",
            "options": ["Very Poor", "Poor", "Fair", "Good", "Very Good", "Excellent"]
        },
        {
            "id": "illness",
            "label": "Have you been severely ill in the last year?",
            "type": "radio",
            "options": [{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}]
        },
        {
            "id": "children",
            "label": "Do you have children or are you planning to have children?",
            "type": "radio",
            "options": [{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}]
        }
    ]

    if request.method == 'POST':
        # Get the current question's ID and user's response
        question_id = request.form.get('question_id')
        answer = request.form.get('answer')

        # Initialize session for group preferences if not already done
        if 'preferences' not in session:
            session['preferences'] = {}

        # Store the response using the question's ID
        session['preferences'][question_id] = answer

        # Move to the next question
        current_index = next((i for i, q in enumerate(questions) if q['id'] == question_id), -1)
        next_index = current_index + 1

        if next_index >= len(questions):
            # Save all responses to the database
            try:
                conn = get_db_connection()
                conn.execute('''
                    UPDATE user_responses
                    SET general_health = ?, illness = ?, children = ?
                    WHERE id = (SELECT MAX(id) FROM user_responses)
                ''', [
                    session['preferences'].get('general_health'),
                    session['preferences'].get('illness'),
                    session['preferences'].get('children'),
                ])
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error saving group preferences: {e}")
                return "An error occurred while saving your responses. Please try again."

            # Clear the session preferences data
            session.pop('preferences', None)
            return redirect('/thank-you')

        # Redirect to the next question
        return redirect(f'/group-preferences?index={next_index}')

    # Get the current question based on the index in the query parameter
    current_index = int(request.args.get('index', 0))
    question = questions[current_index]
    return render_template('group_preferences.html', question=question, index=current_index)


# Route to thank users after survey submission
@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html', language=session.get('language'))


# Route for no consent page
@app.route('/no-consent')
def no_consent():
    return render_template('no_consent.html', language=session.get('language'))


# Route for admin login
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin':
            session['admin'] = True
            return redirect('/results')
        else:
            return "Incorrect password. Try again."
    return render_template('admin_login.html', language=session.get('language'))


@app.route('/results')
def results():
    if 'admin' in session:
        # Connect to the database
        conn = get_db_connection()

        # Fetch all user responses
        user_responses = conn.execute('SELECT * FROM user_responses').fetchall()
        conn.close()

        # Render the results page with user responses
        return render_template('results.html', user_responses=user_responses)

    # If the user is not logged in as admin, redirect to admin login
    return redirect('/admin')

from flask import Response
import csv

@app.route('/download-csv')
def download_csv():
    if 'admin' in session:
        # Connect to the database
        conn = get_db_connection()
        user_responses = conn.execute('SELECT * FROM user_responses').fetchall()
        conn.close()

        # Prepare the CSV content
        def generate_csv():
            # Create a CSV output
            output = []
            # Write header row (column names)
            output.append(",".join([key for key in user_responses[0].keys()]))

            # Write each row
            for row in user_responses:
                output.append(",".join([str(row[key]) for key in row.keys()]))

            return "\n".join(output)

        # Generate the CSV content
        csv_content = generate_csv()

        # Create a Response object for the CSV file
        response = Response(csv_content, mimetype='text/csv')
        response.headers.set("Content-Disposition", "attachment", filename="survey_results.csv")
        return response

    return redirect('/admin')  # Redirect to admin login if not logged in



# Route to logout admin
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/admin')


if __name__ == '__main__':
    app.run(debug=True)

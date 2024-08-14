from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

@app.route("/")
def home():
    return render_template("resume.html")



@app.route('/send_message', methods=['POST'])
def send_message_route():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    # Check if all fields are completed
    if not name or not email or not message:
        flash('All fields are required!', 'danger')
        return redirect(url_for('resume.html'))

    # Combine name, email, and message into a single string to return
    full_message = f"Name: {name}\nEmail: {email}\nMessage: {message}"

    try:
        # Create the email content
        msg = MIMEMultipart()
        msg['From'] = os.getenv('GMAIL_USERNAME')
        msg['To'] = os.getenv('GMAIL_USERNAME')
        msg['Subject'] = "Resume Website Contact Submission"

        # Attach the message
        msg.attach(MIMEText(full_message, 'plain'))

        # Connect to the server and send the email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(os.getenv('GMAIL_USERNAME'), os.getenv('GOOGLE_PASSWORD'))  # Hide before GitHub push
        server.send_message(msg)
        server.quit()

        flash('Message sent successfully!', 'success')
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
        flash(f'Failed to send message. Error: {str(e)}', 'danger')
    except Exception as e:
        print(f"An error occurred: {e}")
        flash(f'Failed to send message. Error: {str(e)}', 'danger')

    return redirect(url_for('home'))



@app.route('/chat_assistant', methods=['POST'])
def chat_assistant_route():
    user_message = request.json.get("message")

    loader = WebBaseLoader("https://calm-refuge-84210-53bd9dafdd04.herokuapp.com")
    docs = loader.load()

    docs_json = [{'url': doc.metadata.get('url'), 'content': doc.page_content} for doc in docs]

    client = OpenAI(
        # This is the default and can be omitted
        api_key = os.getenv('OPENAI_API_KEY')
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"You are a chatbot for a resume website. Answer all questions about S'Bussiso Dube based off of this information: {docs_json}"
            },
            {
                "role": "user",
                "content": user_message,
            }
        ],
        model="gpt-3.5-turbo",
    )
    # Access the content using the 'message' attribute of the Choice object
    assistant_message = chat_completion.choices[0].message.content
    print(assistant_message)
    return jsonify({"message": assistant_message})






if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)


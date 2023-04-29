from flask import Flask, render_template, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Google Sheets credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('united-option-379311-32c22a337d18.json', scope)
client = gspread.authorize(creds)
sheet = client.open('WEB_ORDER').sheet1

# Render order form
@app.route('/')
def index():
    return render_template('BomberPage.html')

# Submit order form
@app.route('/', methods=['POST'])
def submit_order():
    # Get form data
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    product_name = request.form['product_name']
    quantity = request.form['quantity']
    order_description = request.form['order_description']
    payment_proof = request.files['payment_proof']

    # Save payment proof to Google Drive
    file_name = payment_proof.filename
    payment_proof.save(file_name)
    drive_folder_id = '1te4a3TstjVeLBuTqvcogt0IPl9kaSnbN'
    file_metadata = {'name': file_name, 'parents': [drive_folder_id]}
    media = googleapiclient.http.MediaFileUpload(file_name, resumable=True)
    drive_service = build('drive', 'v3', credentials=creds)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')

    # Save order data to Google Sheets
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    order_data = [current_date, name, email, phone, product_name, quantity, order_description, file_id]
    sheet.insert_row(order_data, 2)

    # Render confirmation page
    return render_template('success.html')

if __name__ == '__main__':
    app.run()

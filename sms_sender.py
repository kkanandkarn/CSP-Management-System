from twilio.rest import Client

# Your Twilio account SID and auth token
account_sid = 'ACcfa7ed97949bb58abe841bfea67f1bc6'
auth_token = '3cff29f4b95cb7155ce10594a6c46be0'

# Create a Twilio client
client = Client(account_sid, auth_token)

# Sending an SMS
message = client.messages.create(
    from_='+13613493910',
    body='your otp is 5834',
    to='+919262261560'
)

print(f"SMS sent successfully. SID: {message.sid}")

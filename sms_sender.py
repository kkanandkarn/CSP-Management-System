from twilio.rest import Client

# Your Twilio account SID and auth token
account_sid = 'twilio account_sid'
auth_token = 'twilio auth_token'

# Create a Twilio client
client = Client(account_sid, auth_token)

# Sending an SMS
message = client.messages.create(
    from_='+13613493910',
    body='your otp is 5834',
    to='+919262261560'
)

print(f"SMS sent successfully. SID: {message.sid}")

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.models.consumer.access_manager import PNAccessManagerAuditResult
from pubnub.models.consumer.v3.channel import Channel
from pubnub.models.consumer.v3.group import Group
from pubnub.models.consumer.v3.uuid import UUID
import time, os

# PubNub configuration
def initialize_pubnub(uuid):
    if not uuid:
        raise ValueError("UUID cannot be empty or None.")
    
    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
    pnconfig.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
    pnconfig.secret_key = os.getenv("PUBNUB_SECRET_KEY")
    pnconfig.uuid = os.getenv("PUBNUB_USER_ID")
    return PubNub(pnconfig)

    
def generate_token(user_id, ttl=5):
    try:
        pubnub = initialize_pubnub(user_id)
        
        print(f"Granting token for user_id: {user_id}")
        
        envelope = pubnub.grant_token() \
            .channels([Channel.id("elgas_pi_channel").read().write()]) \
            .authorized_uuid(user_id) \
            .ttl(ttl) \
            .sync() 
        
        token = envelope.result.token 
        print(token)
        return token
    except Exception as e:
        print(f"Error generating token: {e}")
        return None

def parse_token(token, user_id):
    try:
        print("Parsing the TOKEN")

        pubnub = initialize_pubnub(user_id)

        token_details = pubnub.parse_token(token)
        
        read_access = token_details.resources.channels["elgas_pi_channel"]["read"]
        write_access = token_details.resources.channels["elgas_pi_channel"]["write"]
        uuid = token_details.authorized_uuid
        ttl = token_details.ttl
        timestamp = token_details.timestamp

        print(f"Token Details: UUID={uuid}, TTL={ttl}, Timestamp={timestamp}")
        print(f"Read Access: {read_access}, Write Access: {write_access}")
        
        return timestamp, ttl, uuid, read_access, write_access
    except Exception as e:
        print(f"Error parsing token: {e}")
        return None
    
def refresh_token(user_id, ttl=5):
    try:
        new_token = generate_token(user_id, ttl=ttl)
        if new_token:
            print(f"Token refreshed successfully for user: {user_id}")
        else:
            print(f"Failed to refresh token for user: {user_id}")
        return new_token
    except Exception as e:
        print(f"Error in refresh_token: {e}")
        return None
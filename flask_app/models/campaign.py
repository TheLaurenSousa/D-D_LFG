from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
db = "danddlfg"

class Campaign:
    def __init__( self , data ):
        self.id = data['id']
        self.name = data['name']
        self.format = data['format']
        self.num_players = data['num_players']
        self.accepted_players = data['accepted_players']
        self.availability = data['availability']
        self.description = data['description']
        self.status = data['status']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def new_campaign(cls, data):
        query = "INSERT INTO campaigns (name, format, num_players, availability, description, status) VALUES (%(name)s, %(format)s, %(num_players)s, %(availability)s, %(description)s, 'Open');"
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def close_campaign(cls, data):
        query = "UPDATE campaigns SET status = 'Closed' WHERE id = %(campaign_id)s;"
        return connectToMySQL(db).query_db(query, data)
    
    @classmethod
    def open_campaign(cls, data):
        query = "UPDATE campaigns SET status = 'Open' WHERE id = %(campaign_id)s;"
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def add_user_to_campaign(cls, data):
        query = "INSERT INTO campaign_users (user_id, campaign_id, role, status) VALUES (%(user_id)s, %(campaign_id)s, %(role)s, %(status)s);"
        return connectToMySQL(db).query_db(query, data)
    
    @classmethod
    def remove_user_from_campaign(cls, data):
        query = "DELETE from campaign_users WHERE campaign_id = %(campaign_id)s AND user_id = %(user_id)s;"
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def accept_user_to_campaign(cls, data):
        playerQuery = "UPDATE campaigns SET accepted_players = accepted_players+1 WHERE id = %(campaign_id)s;"
        results = connectToMySQL(db).query_db(playerQuery, data)
        query = "UPDATE campaign_users SET status = 'Accepted' WHERE user_id = %(user_id)s AND campaign_id = %(campaign_id)s;"
        return connectToMySQL(db).query_db(query, data)
    
    @classmethod
    def reject_user_to_campaign(cls, data):
        playerQuery = "UPDATE campaigns SET accepted_players = accepted_players-1 WHERE id = %(campaign_id)s;"
        results = connectToMySQL(db).query_db(playerQuery, data)
        query = "UPDATE campaign_users SET status = 'Rejected' WHERE user_id = %(user_id)s AND campaign_id = %(campaign_id)s;"
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def count_accepted_players(cls, data):
        query = "SELECT * FROM campaign_users WHERE campaign_id = 1 and status = 'accepted';"
        results = connectToMySQL(db).query_db(query, data)
        accepted_players = 0
        for row in results:
            accepted_players += 1
        return accepted_players

    @classmethod
    def get_campaigns_by_user_id(cls, data):
        query = "SELECT campaign_users.user_id AS user_id, campaign_users.campaign_id AS campaign_id, campaigns.name AS name, campaign_users.role AS role, campaigns.num_players AS num_players, campaigns.accepted_players as accepted_players, campaigns.status AS campaign_status, campaign_users.status AS user_status FROM campaign_users LEFT JOIN campaigns ON campaign_users.campaign_id = campaigns.id WHERE user_id = %(user_id)s AND campaign_users.status != 'rejected';"
        results = connectToMySQL(db).query_db(query, data)
        campaigns = []
        for row in results:
            campaign_data = {
                "name": row['name'],
                "role": row['role'],
                "accepted_players": row['accepted_players'],
                "num_players": row['num_players'],
                "status": row['campaign_status'],
                "campaign_id": row['campaign_id']
            }
            campaigns.append(campaign_data)
        return campaigns

    @classmethod
    def check_user_status(cls, data):
        query = "SELECT campaign_users.user_id AS user_id, campaign_users.campaign_id AS campaign_id, campaigns.name AS name, campaign_users.role AS role, campaigns.num_players AS num_players, campaigns.status AS campaign_status, campaign_users.status AS user_status FROM campaign_users LEFT JOIN campaigns ON campaign_users.campaign_id = campaigns.id WHERE user_id = %(user_id)s AND campaign_id = %(campaign_id)s;"
        results = connectToMySQL(db).query_db(query, data)
        if results == True and results[0]['user_status'] == "Rejected":
            return False
        else:
            return True

    @classmethod
    def get_campaign_by_id(cls, data):
        query = "SELECT * FROM campaigns WHERE id= %(campaign_id)s;"
        results = connectToMySQL(db).query_db(query, data)
        return cls(results[0])

    @classmethod
    def get_open_campaigns(cls):
        query = "SELECT * FROM campaigns WHERE status = 'open';"
        results = connectToMySQL(db).query_db(query)
        campaigns = []
        for row in results:
            campaign_data = {
                "campaign_id": row['id'],
                "name": row['name'],
                "format": row['format'],
                "accepted_players": row['accepted_players'],
                "num_players": row['num_players']
            }
            campaigns.append(campaign_data)
        return campaigns

    @classmethod
    def get_players_for_campaign(cls, data):
        players = []
        query = "SELECT users.id AS user_id, campaign_users.campaign_id as campaign_id, users.name AS name, campaign_users.role AS role, campaign_users.status AS status, player_info.availability AS availability, player_info.experience AS experience, player_info.class1 AS class1, player_info.class2 AS class2, player_info.class3 AS class3, player_info.bio as bio FROM campaign_users LEFT JOIN campaigns ON campaign_users.campaign_id = campaigns.id LEFT JOIN users ON users.id = campaign_users.user_id LEFT JOIN player_info ON player_info.id = users.id WHERE campaign_users.campaign_id = %(campaign_id)s AND ((role = 'player' AND campaign_users.status = 'Applied') OR (role = 'player' AND campaign_users.status = 'Accepted'));"
        results = connectToMySQL(db).query_db(query, data)
        for row in results:
            player_data = {
                "id": row['user_id'],
                "name": row['name'],
                "role": row['role'],
                "status": row['status'],
                "availability": row['availability'],
                "experience": row['experience'],
                "class1": row['class1'],
                "class2": row['class2'],
                "class3": row['class3'],
                "bio": row['bio']
            }
            players.append(player_data)
        return players

    @classmethod
    def get_dm_for_campaign(cls, data):
        dm = []
        query = "SELECT users.id AS dm_id, users.name AS name, campaign_users.role AS role, dm_info.availability AS availability, dm_info.experience AS experience, dm_info.bio as bio FROM campaign_users LEFT JOIN campaigns ON campaign_users.campaign_id = campaigns.id LEFT JOIN users ON users.id = campaign_users.user_id LEFT JOIN dm_info ON dm_info.user_id = users.id WHERE campaign_id = %(campaign_id)s AND role = 'dm';"
        results = connectToMySQL(db).query_db(query, data)
        for row in results:
            dm_data = {
                "id": row['dm_id'],
                "name": row['name'],
                "role": row['role'],
                "availability": row['availability'],
                "experience": row['experience'],
                "bio": row['bio']
            }
            dm.append(dm_data)
        return dm[0]

    @classmethod
    def user_in_campaign(cls, data):
        player_list = Campaign.get_players_for_campaign(data)
        dm_info = Campaign.get_dm_for_campaign(data)
        for row in player_list:
            if row['id'] == data['user_id']:
                return True
        if dm_info['id'] == data['user_id']:
            return True
        return False

    @classmethod
    def user_campaign_status(cls, data):
        query = "SELECT * FROM campaign_users WHERE user_id = %(user_id)s;"
        results = connectToMySQL(db).query_db(query, data)
        if len(results) == 0:
            return False
        return results[0]

    @classmethod
    def get_campaign_messages(cls, data):
        query = "SELECT campaign_messages.id AS message_id, campaign_messages.user_id AS user_id, campaign_messages.campaign_id AS campaign_id, content AS content, users.name AS commenter_name, campaign_messages.created_at AS created_at, campaign_messages.updated_at AS updated_at FROM campaign_messages LEFT JOIN users ON campaign_messages.user_id = users.id WHERE campaign_id = %(campaign_id)s;"
        results = connectToMySQL(db).query_db(query, data)
        messages = []
        for row in results:
            message_data = {
                "message_id": row['message_id'],
                "user_id": row['user_id'],
                "campaign_id": row['campaign_id'],
                "content": row['content'],
                "commenter_name": row['commenter_name']
            }
            messages.append(message_data)
        return messages

    @classmethod
    def publish_message(cls, data):
        query = "INSERT INTO campaign_messages (user_id, campaign_id, content) VALUES (%(user_id)s, %(campaign_id)s, %(content)s);"
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def delete_message(cls, data):
        query = "DELETE FROM campaign_messages WHERE id=%(message_id)s;"
        return connectToMySQL(db).query_db(query, data)

    @staticmethod
    def validate_new_campaign(data):
        is_valid = True
        if len(data['name']) == 0 or len(data['format']) == 0 or len(data['num_players']) == 0 or len(data['availability']) == 0 or len(data['description']) == 0:
            is_valid = False
            flash("All fields are required.", "campaign")
        if data['format'] == "unselected":
            is_valid = False
            flash("Make sure to select a valid format.", "campaign")
        if data['num_players'] == "unselected":
            is_valid = False
            flash("Make sure to select a valid number of players.", "campaign")
        return is_valid

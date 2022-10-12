from flask import render_template,redirect,request, session, flash
from flask_app import app
from flask_app.models.user import User
from flask_app.models.campaign import Campaign



@app.route("/dashboard") #User Dashboard
def dashboard():
    if 'id' not in session:
        return redirect("/logout")
    data = {
        "user_id": session['id']
    }
    return render_template("dashboard.html", user_campaigns = Campaign.get_campaigns_by_user_id(data), gmStatus = User.get_dm_status_by_id(data))

@app.route("/campaigns") #Redirects to the User Dashboard in case someone changes the slug
def campaigns():
    if 'id' not in session:
        return redirect("/logout")
    return redirect("/dashboard")

@app.route("/campaigns/new") #DM creates a new campaign
def new_campaign():
    if 'id' not in session:
        return redirect("/logout")
    data = {
        "user_id": session['id']
    }
    checker = User.get_dm_status_by_id(data)
    if checker == True:
        return render_template("new_campaign.html", gmStatus = User.get_dm_status_by_id(data))
    else:
        return redirect("/dashboard")

@app.route("/campaigns/create", methods=["Post"]) #Submit new campaign
def create_campaign():
    if not Campaign.validate_new_campaign(request.form):
        return redirect('/campaigns/new')
    data = {
        "name": request.form['name'],
        "format": request.form['format'],
        "num_players": request.form['num_players'],
        "availability": request.form['availability'],
        "description": request.form['description'],
    }
    campaign_id = Campaign.new_campaign(data)
    connection = {
        "user_id": request.form['user_id'],
        "campaign_id": campaign_id,
        "role": "DM",
        "status": "DM"
    }
    Campaign.add_user_to_campaign(connection)
    return redirect("/dashboard")

@app.route("/campaigns/all") #All open campaigns
def all_campaigns():
    if 'id' not in session:
        return redirect("/logout")
    data = {
        "user_id": session['id']
    }
    return render_template("all_campaigns.html", open_campaigns = Campaign.get_open_campaigns(), gmStatus = User.get_dm_status_by_id(data))

@app.route("/campaigns/<int:id>") #View an existing campaign
def view_campaign(id):
    if 'id' not in session:
        return redirect("/logout")
    data = {
        "campaign_id": id,
        "user_id": session['id']
    }
    return render_template("campaign.html", campaign_info = Campaign.get_campaign_by_id(data), player_info = Campaign.get_players_for_campaign(data), dm_info = Campaign.get_dm_for_campaign(data), user_in_campaign = Campaign.user_in_campaign(data), user = Campaign.user_campaign_status(data), all_messages = Campaign.get_campaign_messages(data), gmStatus = User.get_dm_status_by_id(data))

@app.route("/campaigns/add/<int:campaign_id>/<int:user_id>") #User adds self to campaign
def add_user_to_campaign(campaign_id, user_id):
    data = {
        "user_id": user_id,
        "campaign_id": campaign_id,
        "role": 'Player',
        "status": 'Applied'
    }
    if Campaign.check_user_status(data):
        Campaign.add_user_to_campaign(data)
        return redirect(f"/campaigns/{campaign_id}")
    else:
        return redirect("/dashboard")

@app.route("/campaigns/remove/<int:campaign_id>/<int:user_id>") #User removes self from campaign
def remove_user_from_campaign(campaign_id, user_id):
    data = {
        "user_id": user_id,
        "campaign_id": campaign_id,
    }
    Campaign.remove_user_from_campaign(data)
    return redirect(f"/campaigns/{campaign_id}")

@app.route("/campaigns/accept/<int:campaign_id>/<int:user_id>") #DM Approves User for campaign
def accept_user_to_campaign(campaign_id, user_id):
    data = {
        "user_id": user_id,
        "campaign_id": campaign_id,
    }
    Campaign.accept_user_to_campaign(data)
    return redirect(f"/campaigns/{campaign_id}")

@app.route("/campaigns/reject/<int:campaign_id>/<int:user_id>") #DM Rejects User for campaign
def reject_user_to_campaign(campaign_id, user_id):
    data = {
        "user_id": user_id,
        "campaign_id": campaign_id,
    }
    Campaign.reject_user_to_campaign(data)
    return redirect(f"/campaigns/{campaign_id}")

@app.route("/publish_message/<int:campaign_id>", methods=["Post"]) #User posts a message
def publish_message(campaign_id):
    data = {
        "user_id": request.form['user_id'],
        "campaign_id": campaign_id,
        "content": request.form['content']
    }
    Campaign.publish_message(data)
    return redirect(f"/campaigns/{campaign_id}")

@app.route("/delete_message/<int:campaign_id>/<int:message_id>") #User deletes a message
def delete_message(campaign_id, message_id):
    data = {
        "message_id": message_id
    }
    Campaign.delete_message(data)
    return redirect(f"/campaigns/{campaign_id}")

@app.route("/campaigns/close/<int:campaign_id>") #DM closes a campaign to applicants
def close_campaign(campaign_id):
    data = {
        "campaign_id": campaign_id
    }
    Campaign.close_campaign(data)
    return redirect(f"/campaigns/{campaign_id}")

@app.route("/campaigns/open/<int:campaign_id>") #DM opens a campaign to applicants
def open_campaign(campaign_id):
    data = {
        "campaign_id": campaign_id
    }
    Campaign.open_campaign(data)
    return redirect(f"/campaigns/{campaign_id}")
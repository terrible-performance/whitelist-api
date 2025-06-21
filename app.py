from flask import Flask, request, jsonify, Response
import os

app = Flask(__name__)
WHITELIST_FILE = "whitelist.lua"

def parse_userids(lua_content):
    userids = []
    for line in lua_content.splitlines():
        line = line.strip().strip(",")
        if line.isdigit():
            userids.append(int(line))
    return userids

def generate_lua(userids):
    lines = ["return {"]
    for uid in sorted(set(userids)):
        lines.append(f"    {uid},")
    lines.append("}")
    return "\n".join(lines)

@app.route("/add-whitelist", methods=["POST"])
def add_whitelist():
    data = request.get_json()
    if not data or "user_id" not in data:
        return jsonify({"error": "Missing user_id"}), 400

    user_id = data["user_id"]
    if not isinstance(user_id, int):
        return jsonify({"error": "user_id must be an integer"}), 400

    # Read existing whitelist
    if os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, "r") as f:
            content = f.read()
        userids = parse_userids(content)
    else:
        userids = []

    if user_id in userids:
        return jsonify({"message": "User already whitelisted"}), 200

    userids.append(user_id)
    new_lua = generate_lua(userids)

    with open(WHITELIST_FILE, "w") as f:
        f.write(new_lua)

    return jsonify({"message": f"User {user_id} added to whitelist"}), 200

@app.route("/whitelist.lua", methods=["GET"])
def serve_whitelist():
    if not os.path.exists(WHITELIST_FILE):
        return Response("return {}", mimetype='text/plain')
    with open(WHITELIST_FILE, "r") as f:
        return Response(f.read(), mimetype='text/plain')

if __name__ == "__main__":
    app.run()

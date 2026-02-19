% spotify_update.m
% Runs headless in GitHub Actions

client_id     = getenv("SPOTIFY_CLIENT_ID");
client_secret = getenv("SPOTIFY_CLIENT_SECRET");
refresh_token = getenv("SPOTIFY_REFRESH_TOKEN");

assert(~isempty(client_id), "Missing client ID");
assert(~isempty(client_secret), "Missing client secret");
assert(~isempty(refresh_token), "Missing refresh token");

% === Refresh access token ===
auth_str = matlab.net.base64encode(client_id + ":" + client_secret);
headers = matlab.net.http.HeaderField("Authorization", "Basic " + auth_str);

body = matlab.net.QueryParameter( ...
    "grant_type","refresh_token", ...
    "refresh_token",refresh_token ...
);

req = matlab.net.http.RequestMessage("POST", headers, body);
resp = req.send("https://accounts.spotify.com/api/token");

if isstruct(resp.Body.Data)
    tokens = resp.Body.Data;
else
    tokens = jsondecode(char(resp.Body.Data));
end

access_token = tokens.access_token;

% === Fetch recently played ===
headers = matlab.net.http.HeaderField("Authorization", "Bearer " + access_token);
req = matlab.net.http.RequestMessage("GET", headers);

url = "https://api.spotify.com/v1/me/player/recently-played?limit=50";
resp = req.send(url);

if isstruct(resp.Body.Data)
    new_data = resp.Body.Data;
else
    new_data = jsondecode(char(resp.Body.Data));
end

% === Load existing history ===
json_file = "listening_history.json";

if isfile(json_file)
    old = jsondecode(fileread(json_file));
    old_items = old.items;
else
    old_items = [];
end

% === Append only new plays ===
all_items = old_items;
old_times = {};
if ~isempty(old_items)
    old_times = {old_items.played_at};
end

for i = 1:length(new_data.items)
    t = new_data.items(i).played_at;
    if ~ismember(t, old_times)
        all_items(end+1) = new_data.items(i); %#ok<SAGROW>
    end
end

updated.items = all_items;

fid = fopen(json_file, "w");
fwrite(fid, jsonencode(updated), "char");
fclose(fid);

disp("Spotify history updated successfully");

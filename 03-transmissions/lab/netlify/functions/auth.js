// Minimal GitHub OAuth proxy for Decap CMS's "github" backend (see public/admin/config.yml's
// auth_endpoint). Two roles depending on the request, both handled at this one URL:
//
// 1. No `code` in the query string -- this is the START of login. Redirect to GitHub's own
//    OAuth authorize page, telling GitHub to send the user back to this SAME function once
//    they approve.
// 2. A `code` IS present -- GitHub just redirected back here. Exchange that code for a real
//    access token (server-side, using the app's secret -- this is the one step that can't
//    happen in the browser) and hand the token to the Decap admin page that opened this as a
//    popup, via the exact postMessage handshake Decap's github backend expects.
//
// Needs two environment variables set in the hosting dashboard (Netlify): OAUTH_CLIENT_ID
// and OAUTH_CLIENT_SECRET, from the GitHub OAuth App -- see README.md for the exact setup
// steps. Never commit those values here.
const CLIENT_ID = process.env.OAUTH_CLIENT_ID;
const CLIENT_SECRET = process.env.OAUTH_CLIENT_SECRET;

exports.handler = async (event) => {
  const redirectUri = `https://${event.headers.host}/.netlify/functions/auth`;
  const code = event.queryStringParameters && event.queryStringParameters.code;

  if (!code) {
    const authorizeUrl = new URL("https://github.com/login/oauth/authorize");
    authorizeUrl.searchParams.set("client_id", CLIENT_ID);
    authorizeUrl.searchParams.set("scope", "repo,user");
    authorizeUrl.searchParams.set("redirect_uri", redirectUri);

    return {
      statusCode: 302,
      headers: { Location: authorizeUrl.toString() },
      body: "",
    };
  }

  const tokenResponse = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      code,
      redirect_uri: redirectUri,
    }),
  });
  const tokenData = await tokenResponse.json();

  if (tokenData.error) {
    return {
      statusCode: 401,
      body: `GitHub OAuth error: ${tokenData.error_description || tokenData.error}`,
    };
  }

  const payload = JSON.stringify({ token: tokenData.access_token, provider: "github" });

  const html = `<!doctype html>
<html><body>
<script>
  (function() {
    function receiveMessage(e) {
      window.opener.postMessage(
        'authorization:github:success:${payload.replace(/'/g, "\\'")}',
        e.origin
      );
      window.removeEventListener("message", receiveMessage, false);
    }
    window.addEventListener("message", receiveMessage, false);
    window.opener.postMessage("authorizing:github", "*");
  })();
</script>
</body></html>`;

  return {
    statusCode: 200,
    headers: { "Content-Type": "text/html" },
    body: html,
  };
};

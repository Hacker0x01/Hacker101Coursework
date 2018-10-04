
Level0
======

Cross-Site Request Forgery
--------------------------

**Severity**: Critical

**Description**: The "Transfer Funds" functionality is vulnerable to CSRF due to no session-specific random token being attached to the form.

**Reproduction Steps**:

1. Go to the Transfer Funds page
2. Submit a funds transfer
3. Note that the only data transmitted is the destination and the amount.

You can also use the following proof of concept to submit an automatic transfer:

	<body onload="document.forms[0].submit()">
		<form action="http://breaker-studentcenter.appspot.com/levels/0/" method="POST">
			<input type="hidden" name="amount" value="1000000">
			<input type="hidden" name="to" value="1625">
		</form>
	</body>

**Impact**: Due to the simple nature of this vulnerability, it's possible for an attacker to transfer funds from any victim whom he can convince to access a page controlled by the attacker.  In this proof of concept, it's done via form autosubmission in plain view, but this could be performed in a hidden IFrame, leaving the user no clue that an attack has happened at all.

**Mitigation**: Proper CSRF tokens should be used on all forms.  You can read more here: https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF)

**Affected Assets**: http://breaker-studentcenter.appspot.com/levels/0

Reflected XSS
-------------

**Severity**: Critical

**Description**: The `amount` field of transfers is vulnerable to reflected XSS due to a lack of safe escaping.
This can be triggered via GET (to auto-fill the `to` and `amount` fields) or via error cases on POST.

**Reproduction Steps**:

1. Go to the Transfer Funds page
2. Enter anything into the `to` field and in the amount field enter `"><script>alert(1);</script>`
3. Submit the transfer
4. Note that a script tag has been added to the page; depending on XSS protection settings, you may see an alert box as well

**Impact**: This vulnerability allows an attacker to perform any tasks she desires, as an arbitrary user whom she convinces to click a link containing an XSS payload.
This means that an attacker could distribute a payload that causes any user to transfer money to her.

**Mitigation**: All user input must be escaped before displaying to the page, in order to properly mitigate XSS issues.
In this case, it may also be a good idea to convert the amount value to an integer first, as this would completely eliminate the possibility of user input compromising the page.

**Affected Assets**: http://breaker-studentcenter.appspot.com/levels/0

Direct Object Reference
-----------------------

**Severity**: Critical

**Description**: In addition to the normal `to` field on transfers, the `from` field is also accepted, allowing you to specify the account you're transferring from; authentication for the accounts is not required.

**Reproduction Steps**:

The following proof of concept performs an automatic transfer from account 1 to account 2, regardless of whether or not you are logged into either account:

	<body onload="document.forms[0].submit()">
		<form action="http://breaker-studentcenter.appspot.com/levels/0/" method="POST">
			<input type="hidden" name="amount" value="1000000">
			<input type="hidden" name="from" value="1">
			<input type="hidden" name="to" value="2">
		</form>
	</body>

**Impact**: Due to the lack of authorization and the ability to directly reference accounts, this makes it trivial for an attacker to transfer funds between any account.

**Mitigation**: The `from` field should be ignored or -- at the very least -- checked against the account(s) attached to the logged in user.

**Affected Assets**: http://breaker-studentcenter.appspot.com/levels/0

Level1
=======

CSRF Tokens Validated Improperly
--------------------------------

**Severity**: Medium

**Description**: While the application uses CSRF tokens, its only validation for them is to ensure that they are 32 characters long.  This check is inadequate as any CSRF token (or, indeed, any string of the proper length) will pass the check.

**Reproduction Steps**:

1. Submit a wall post
2. Intercept the post with Burp Proxy
3. Change the CSRF token to any other value
4. Note that the post was successful

**Impact**: Due to the simple nature of this vulnerability, it's possible for an attacker to post to the wall of any victim whom he can convince to access a page controlled by the attacker.

**Mitigation**: CSRF tokens must be compared in entirety, preferably in constant time to reduce the likelihood of timing attacks.

**Affected Assets**: http://breaker-studentcenter.appspot.com/levels/1

CSRF Tokens Easily Guessed
--------------------------

**Severity**: Medium

**Description**: While the application uses CSRF tokens, they are not generated randomly, as per standard practice.  Instead, they are generated as the MD5 of the user's account nickname.  This makes it trivial to guess the CSRF token and falsify it for targeted attacks.

**Reproduction Steps**:

1. Look at the CSRF token on the page
2. Run the command `echo -n your.nickname | md5sum` at the command line
3. Note that the output of this command matches the CSRF token

**Impact**: Due to the ease with which these tokens can be guessed, it is trivial for an attacker to perform targeted attacks against a given user.

**Mitigation**: CSRF tokens must be generated randomly upon creation of each user's session.

**Affected Assets**: http://breaker-studentcenter.appspot.com/levels/1

Stored XSS
----------

**Severity**: Medium

**Description**: Due to improper handling of links, it's possible to embed stored XSS payloads in wall posts.

**Reproduction Steps**:

1. Submit a wall post including the URL `http://google.com"onmousover="alert(1)`
2. Hover over the link in the submitted post
3. Note that an alert dialog is triggered

**Impact**: Stored XSS here makes it possible for an attacker to easily impersonate a user's behavior.  Due to the fact that the attacker could force a user to make new posts, it's possible that self-sustaining malware could be distributed utilizing this vulnerability.

**Mitigation**: All user input -- including these links -- must be properly HTML escaped before output.

**Affected Assets**: http://breaker-studentcenter.appspot.com/levels/1

Forced Browsing/Enumerable Post IDs
-----------------------------------

**Severity**: Low

**Description**: Due to the use of incremental IDs and a lack of authorization checks, it's possible for users to enumerate the posts of others.

**Reproduction Steps**:

1. View the page http://breaker-studentcenter.appspot.com/levels/1/post?id=0
2. Note that you see a post by cody.brocious
3. http://breaker-studentcenter.appspot.com/levels/1/post?id=1
4. Note that you see a post by another user
5. Continuing to increment the id will give you every post in the system.

**Impact**: An attacker can trivially read every single post in the system, regardless of the user's privacy.

**Mitigation**: If the intention is for posts to be private by default, authorization checks should be put in place to ensure that users are unable to access posts outside their permissions.
In addition, IDs generated in a pseudo-random fashion would eliminate the ability to increment the IDs.
Note well that neither of these conditions is sufficient to completely mitigate the issue; if users are still able to access posts without proper authorization, they can do so even if they can't easily guess post IDs.

**Affected Assets**: http://breaker-studentcenter.appspot.com/levels/1


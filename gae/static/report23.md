Level2
======

Reflected XSS
-------------

**Severity**: Medium

**Description**: The application receives an `id` field in the query string.  In the case of viewing a non-existent profile, this field is not properly encoded before display to the user.  In the case of editing profiles, it is ignored but reflected in a non-safe form to the browser as part of the form action.

**Reproduction Steps**:

1. Go to http://breaker-studentcenter.appspot.com/levels/2/?id=%3Cscript%3Ealert(1);%3C/script%3E
2. Note that an alert dialog is shown

**Impact**: This vulnerability allows an attacker to perform any tasks she desires, as an arbitrary user whom she convinces to click a link containing an XSS payload.

**Mitigation**: All user input must be escaped before displaying to the page, in order to properly mitigate XSS issues.
In this case, it is also a good idea to convert the `id` parameter to an integer first, as this would completely eliminate the possibility of user input compromising the page.

**Affected Assets**:

1. http://breaker-studentcenter.appspot.com/levels/2
2. http://breaker-studentcenter.appspot.com/levels/2/edit

Stored XSS
-----------------------

**Severity**: Medium

**Description**: The URL for profile photos is not escaped for display, making it vulnerable to stored XSS on both the profile view and edit pages.

**Reproduction Steps**:

1. Go to the application's edit profile page
2. In the `Profile picture URL` field, insert the following: `http://breaker-studentcenter.appspot.com/favicon.png?"><script>alert(1);</script>.png`
3. Note that the alert dialog is shown upon save

**Impact**: This vulnerability allows an attacker to perform any tasks she desires, as an arbitrary user whom she convinces to click a link containing an XSS payload.

**Mitigation**: All user input must be escaped before displaying to the page, in order to properly mitigate XSS issues.

**Affected Assets**: http://breaker-studentcenter.appspot.com/levels/2/edit

Stored XSS
-----------------------

**Severity**: Medium

**Description**: Colors embedded in the description field of profiles are not escaped when being converted for display.

**Reproduction Steps**:

1. Go to the application's edit profile page
2. In the `Description` field, insert the following: `[ red"><script>alert(1);</script> | Exploit ]`
3. Note that the alert dialog is shown upon save

**Impact**: This vulnerability allows an attacker to perform any tasks she desires, as an arbitrary user whom she convinces to click a link containing an XSS payload.

**Mitigation**: All user input must be escaped before displaying to the page, in order to properly mitigate XSS issues.

**Affected Assets**: http://breaker-studentcenter.appspot.com/levels/2/edit

Notes
-----

The vulnerability count in this level is incorrect, with an actual total of 5, not 7 -- it was based on the number of *outputs* rather than *inputs*.

The unrelated bonus was due to the handling of special characters in the description.  If you're curious, check out https://gist.github.com/daeken/6703071 to see how `\x00-\x02` are handled.

Level3
======

Cross-Site Request Forgery
--------------------------

**Severity**: High

**Description**: The "Edit Page" functionality is vulnerable to CSRF due to no session-specific random token being attached to the form.

**Reproduction Steps**:

1. Go to the admin page
2. Submit a page edit
3. Note that the only data transmitted is the title and the body.

**Impact**: Due to the simple nature of this vulnerability, it's possible for an attacker to perform edits on any page belonging to a victim whom he can convince to access a page controlled by the attacker.

**Mitigation**: Proper CSRF tokens should be used on all forms.  You can read more here: https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF)

**Affected Assets**: http://breaker-studentcenter.appspot.com/levels/3/admin

Lack of Authorization on Admin Functionality
--------------------------------------------

**Severity**: Critical

**Description**: The "Edit Page" functionality only checks admin authorization when accessing the form, but does not check on edits.

**Reproduction Steps**:

1. As a non-admin, perform a POST to http://breaker-studentcenter.appspot.com/levels/3/admin containing the body `title=Vuln&body=No+Admin+Needed`
2. Note that the page is edited to reflect these changes

**Impact**: Due to the lack of authorization, it's possible for any user to perform arbitrary changes to content.  In conjunction with the XSS vulnerabilities, this could allow an attacker to compromise the sessions of every user.

**Mitigation**: Proper authorization must be in place on all actions an administrator could perform.

**Affected Assets**: http://breaker-studentcenter.appspot.com/levels/3/admin

Authorization by Client-Side Credential
---------------------------------------

**Severity**: Critical

**Description**: Authorization for the application is done via a cookie named `admin`.  Changing this from `0` to `1` unlocks all admin functionality.

**Reproduction Steps**:

1. As a non-admin, visit the application while intercepting responses with Burp Proxy
2. When the server sends the `admin` cookie, simply change the value to `1`
3. Note that the page contains admin functionality, which is fully usable

**Impact**: This enables any user to trivially enable administration functionality.

**Mitigation**: User authorization should be stored purely on the server, tied to an authenticated session.

**Affected Assets**: http://breaker-studentcenter.appspot.com/levels/3/

Stored XSS
----------

**Severity**: Medium

**Description**: Due to improper sanitization of page bodies, it's possible to embed stored XSS payloads in pages.

**Reproduction Steps**:

1. As an admin, visit the administration page
2. Put the following in the body: `<a ONmouseover="alert(1)">Hover over me</a>`
3. Save the page
4. Hover over the inserted text and note that an alert dialog is shown

**Impact**: Stored XSS here makes it possible for an attacker to compromise user sessions.

**Mitigation**: All user input must be properly HTML escaped before output.  The use of a third-party, vetted library for HTML sanitization is recommended for tags that should be allowed.

**Affected Assets**: http://breaker-studentcenter.appspot.com/levels/3/admin

Stored XSS
----------

**Severity**: Medium

**Description**: Due to improper sanitization of page titles, it's possible to embed stored XSS payloads in pages.

**Reproduction Steps**:

1. As an admin, visit the administration page
2. Put the following in the title field: `</title><script>alert(1)</script>`
3. Save the page
4. Note that an alert dialog is shown

**Impact**: Stored XSS here makes it possible for an attacker to compromise user sessions.

**Mitigation**: All user input must be properly HTML escaped before output.

**Affected Assets**: http://breaker-studentcenter.appspot.com/levels/3/admin

DOM XSS
-------

**Severity**: Medium

**Description**: Due to improper sanitization of page titles in the window hash, it's possible to inject arbitrary HTML into the page.

**Reproduction Steps**:

1. As an admin, visit the page `http://breaker-studentcenter.appspot.com/levels/3/#home"><script>alert(1);</script>`
2. Note that an alert dialog is shown

**Impact**: This makes it possible for an attacker to compromise the session of an admin user whom she can convince to visit the exploited page.

**Mitigation**: All user input must be properly HTML escaped before output on the client side.

**Affected Assets**: http://breaker-studentcenter.appspot.com/levels/3/

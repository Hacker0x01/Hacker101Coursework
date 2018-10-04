Level4
======

Improper Identity Handling
--------------------------

**Severity**: Low

**Description**: Due to a lack of control over usernames, it is possible for multiple usernames to conflict, appearing as the same user.

**Reproduction Steps**:

1. In your Google Account, change your nickname to `daeken`
2. Make a post on the site
3. Note that it shows up under the name `daeken`, the administrator for the site

**Impact**: It is possible for a malicious user to impersonate another user, leading to confusion.

**Mitigation**: User names should be made unique by storing them locally along with other user data.

**Affected Assets**: Systemic

Systemic Information Disclosures
--------------------------------

**Severity**: Low

**Description**: The application is configured to show tracebacks upon unhandled exceptions, revealing system information.

**Impact**: An attacker may be able to see system paths, code snippets, and other bits of data that could make other attacks easier or viable.

**Mitigation**: Unhandled exceptions should show an "Internal Error" page rather than a traceback.

**Affected Assets**: Systemic

Unchecked Redirects
-------------------

**Severity**: Low

**Description**: The application redirects after submission of votes and deletes using a `from` field in the request.  This can be set to any URL, allowing arbitrary redirection.

**Reproduction Steps**:

1. Go to the delete page for a story you have submitted
2. Change the `from` field in the form to: `http://google.com/`
3. Submit the deletion
4. Note that you are redirected to Google's homepage

**Impact**: An attacker could trick a user into utilizing a fake site, potentially compromising their login credentials.

**Affected Assets**:

1. http://breaker-studentcenter.appspot.com/levels/4/delete
2. http://breaker-studentcenter.appspot.com/levels/4/vote


Reflected XSS
-------------

**Severity**: Medium

**Description**: The application's delete function contains a number of inputs that are not properly escaped: `id`, `type`, and `from`.

**Reproduction Steps**:

1. Go to http://breaker-studentcenter.appspot.com/levels/4/delete?id=4892534685827072&type=Story&from=%22%3E%3Cscript%3Ealert(1)%3B%3C/script%3E
2. Note that an alert dialog is shown

**Impact**: This vulnerability allows an attacker to perform any tasks she desires, as an arbitrary user whom she convinces to click a link containing an XSS payload.

**Mitigation**: All user input must be escaped before displaying to the page, in order to properly mitigate XSS issues.

**Affected Assets**: http://breaker-studentcenter.appspot.com/levels/4/delete

Cross-Site Request Forgery
--------------------------

**Severity**: High

**Description**: The voting and deletion functionality are vulnerable to CSRF due to no session-specific random token being attached to the form.

**Reproduction Steps**:

1. Go to the delete page for a story or comment
2. Note that no CSRF token is included in the request

**Impact**: Due to the simple nature of this vulnerability, it's possible for an attacker to add students to the account of a victim whom he can convince to access a page controlled by the attacker.

**Mitigation**: Proper CSRF tokens should be used on all forms and validated upon submission.  In addition, in the case of voting, state-changing behavior should not be performed via GET.  You can read more here: https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF)

**Affected Assets**:

1. http://breaker-studentcenter.appspot.com/levels/4/delete
1. http://breaker-studentcenter.appspot.com/levels/4/vote

Stored XSS
----------

**Severity**: High

**Description**: The domain field of submitted stories is not properly escaped when being displayed, making it possible to embed stored XSS payloads in pages.  In addition, user nicknames are not escaped for output.

**Reproduction Steps**:

1. Go to http://breaker-studentcenter.appspot.com/levels/4/submit
2. Enter a title and the following URL: `http://google.com<img src="404" onerror="console.log(12345);">`
2. Note that an alert dialog is shown

**Impact**: This vulnerability allows an attacker to perform any tasks she desires, as an arbitrary user whom she convinces to click a link containing an XSS payload.

**Mitigation**: All user input must be escaped before displaying to the page, in order to properly mitigate XSS issues.

**Affected Assets**:

1. http://breaker-studentcenter.appspot.com/levels/4/submit -- Domain XSS
2. http://breaker-studentcenter.appspot.com/levels/4/ and http://breaker-studentcenter.appspot.com/levels/4/comments -- User nicknames

Level5
======

Reflected XSS
-------------

**Severity**: Low

**Description**: The application's browsing and `read` functions receive a `path` field in the query string.  In the case of reading a non-existent file or directory, this field is not properly encoded before display to the user.

**Reproduction Steps**:

1. Go to http://breaker101.herokuapp.com/level5/read?path=nonexistent%3Cscript%3Ealert(1);%3C/script%3E
2. Note that an alert dialog is shown

**Impact**: This vulnerability allows an attacker to perform any tasks she desires, as an arbitrary user whom she convinces to click a link containing an XSS payload.

**Mitigation**: All user input must be escaped before displaying to the page, in order to properly mitigate XSS issues.

**Affected Assets**:

1. http://breaker101.herokuapp.com/level5
2. http://breaker101.herokuapp.com/level5/read

Directory Traversal
-------------------

**Severity**: Critical

**Description**: The directory browsing function of the application is vulnerable to directory traversal in the `path` field, due to a lack of sanitization on user-provided paths.

**Reproduction Steps**:

1. Go to http://breaker101.herokuapp.com/level5?path=../../../../../../etc
2. Note that the contents of the `/etc` directory are shown

**Impact**: This vulnerability allows an attacker to arbitrarily browse the filesystem, revealing the locations and filenames of every file on the system that the web application can access.

**Mitigation**: Paths constructed using user input should have instances of `../` (and `..\`) removed.  Alternatively, detection of such traversal attacks and failing early would potentially make this more resilient.

**Affected Assets**: http://breaker101.herokuapp.com/level5

Directory Traversal
-------------------

**Severity**: Critical

**Description**: The file reading function of the application is vulnerable to directory traversal in the `path` field, due to improper sanitization on user-provided paths.

**Reproduction Steps**:

1. Go to http://breaker101.herokuapp.com/level5/read?path=....//....//....//....//....//....//etc/passwd
2. Note that the contents of the `/etc/passwd` file is shown

**Impact**: This vulnerability allows an attacker to arbitrarily read files from the filesystem, revealing contents of any file on the system that the web application can access.

**Mitigation**: Paths constructed using user input should have instances of `../` (and `..\`) removed.  Alternatively, detection of such traversal attacks and failing early would potentially make this more resilient.

**Affected Assets**: http://breaker101.herokuapp.com/level5/read

Command Injection
-----------------------

**Severity**: Critical

**Description**: Due to a lack of escaping for search queries, it's possible to execute arbitrary commands on the system in the context of the web application.

**Reproduction Steps**:

1. Go to the application
2. In the `Search in directory` field, insert the following: `" | echo "Arbitrary Code`
3. Note that the string "Arbitrary Code" is printed

**Impact**: This vulnerability allows an attacker to execute any command on the server, in the context of the web application.  This allows effectively a complete compromise of any security controls put in place.

**Mitigation**: All user input used in the creation of command lines should be properly quoted and escaped prior to inclusion.  When possible, avoid the construction of command lines using user input entirely.

**Affected Assets**: http://breaker101.herokuapp.com/level5/post_search

Level6
======

Stored XSS
----------

**Severity**: Medium

**Description**: Due to improper sanitization of student last names, it's possible to embed stored XSS payloads in pages.

**Reproduction Steps**:

1. Visit the "Add Student" page of the application
2. Put the following in the `Last name` field: `"><script>alert(1)</script>`
3. Add the student
4. Go to the edit page for the newly added student
5. Note that an alert dialog is shown

**Impact**: Stored XSS here makes it possible for an attacker to compromise user sessions.

**Mitigation**: All user input must be properly HTML escaped before output.

**Affected Assets**: http://breaker101.herokuapp.com/level6/edit

Reflected XSS
-------------

**Severity**: Low

**Description**: Due to a lack of escaping on the `id` field on the rows returned from the database, it is possible for an attacker to embed HTML in pages.

**Reproduction Steps**:

1. As an admin, visit the page `http://breaker101.herokuapp.com/level6?filter=+%27%29+UNION+SELECT+%27%3Cscript%3Ealert%281%29%3B%3C%2Fscript%3E%27%2C+1%2C+1+FROM+students+WHERE+%281%3D1+OR+%27test%27%3D%27`
2. Note that an alert dialog is shown

**Impact**: An attacker could compromise user sessions and execute code in the context of the page.

**Mitigation**: In this case, the SQL injection is what makes this attack possible, so mitigating that issue will fix this as well.  It is also possible (and recommended) that you escape the data returned by the database.

**Affected Assets**: http://breaker101.herokuapp.com/level6

SQL Injection
-------------

**Severity**: Critical

**Description** Due to a lack of escaping on the following fields, it is possible to execute arbitrary SQL in the application.

- ID parameter on the edit page
- `firstname` and `lastname` fields to post_add
- `filter` field on index page

**Reproduction Steps**: See 'Reflected XSS' for an example

**Impact**: An attacker can arbitrarily read and write to the database, compromising data integrity and confidentiality, in addition to potentially escalating privileges to circumvent security controls.

**Affected Assets**:

1. http://breaker101.herokuapp.com/level6
2. http://breaker101.herokuapp.com/level6/post_add
3. http://breaker101.herokuapp.com/level6/edit

Cross-Site Request Forgery
--------------------------

**Severity**: High

**Description**: The "Add Student" functionality is vulnerable to CSRF due to a lack of CSRF token validation.

**Reproduction Steps**:

1. Go to the "Add Students" page
2. Change or modify the CSRF token value in the form
3. Submit the form
4. Note that the student is added despite the token mismatch

**Impact**: Due to the simple nature of this vulnerability, it's possible for an attacker to add students to the account of a victim whom he can convince to access a page controlled by the attacker.

**Mitigation**: Proper CSRF tokens should be used on all forms and validated upon submission.  You can read more here: https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF)

**Affected Assets**: http://breaker101.herokuapp.com/level6/post_add

Level7
======

Reflected XSS
-------------

**Severity**: Low

**Description**: The application shows the previously submitted username and password upon login failure.  The password field is not properly escaped when reflected to the user.

**Reproduction Steps**:

1. Go to http://breaker101.herokuapp.com/level7
2. Submit any username with the password: `"><script>alert(1);</script>`
3. Note that an alert dialog is shown

**Impact**: This vulnerability allows an attacker to perform any tasks she desires, as an arbitrary user whom she convinces to click a link containing an XSS payload.

**Mitigation**: All user input must be escaped before displaying to the page, in order to properly mitigate XSS issues.

**Affected Assets**: http://breaker101.herokuapp.com/level7/post_index

SQL Injection
-------------

**Severity**: Critical

**Description** Due to a lack of escaping on username field, it is possible to execute arbitrary SQL in the application.

**Reproduction Steps**:

1. Go to http://breaker101.herokuapp.com/level7
2. Enter the password `password` and the following username: `' UNION SELECT 'password`
3. Note that you are successfully logged in

**Impact**: An attacker can arbitrarily read and write to the database, compromising data integrity and confidentiality, in addition to potentially escalating privileges to circumvent security controls.

**Affected Assets**: http://breaker101.herokuapp.com/level7/post_index

## ADDED Requirements

### Requirement: User can log in with valid credentials
The system SHALL authenticate a user by verifying the provided username and password against credentials stored in PostgreSQL.

#### Scenario: Successful login
- **WHEN** the user provides a correct username and matching password
- **THEN** the system returns a session token for subsequent operations

#### Scenario: Login with incorrect password
- **WHEN** the user provides a correct username but incorrect password
- **THEN** the system returns an authentication failure error

#### Scenario: Login with non-existent username
- **WHEN** the user provides a username that does not exist in the user store
- **THEN** the system returns an authentication failure error

### Requirement: System validates login input fields
The system SHALL validate that both username and password are provided before attempting authentication.

#### Scenario: Login with missing username
- **WHEN** the user attempts to log in without providing a username
- **THEN** the system returns a validation error indicating username is required

#### Scenario: Login with missing password
- **WHEN** the user attempts to log in without providing a password
- **THEN** the system returns a validation error indicating password is required

### Requirement: Session token persists for authenticated user
The system SHALL store the session token in the PostgreSQL `users` table and allow lookup by token.

#### Scenario: Retrieve current authenticated user
- **WHEN** the system looks up a user by a valid session token
- **THEN** the system returns the username associated with the active session token

### Requirement: Backend exposes a login API endpoint
The system SHALL expose a `POST /api/login` endpoint that accepts JSON credentials and returns a JSON response with a session token on success or an error message on failure.

#### Scenario: API login with valid credentials
- **WHEN** the client sends `POST /api/login` with `{"username": "admin", "password": "password123"}`
- **THEN** the server responds with HTTP 200 and `{"token": "<uuid>"}`

#### Scenario: API login with invalid credentials
- **WHEN** the client sends `POST /api/login` with incorrect username or password
- **THEN** the server responds with HTTP 401 and `{"error": "Invalid username or password"}`

#### Scenario: API login with missing fields
- **WHEN** the client sends `POST /api/login` with missing `username` or `password`
- **THEN** the server responds with HTTP 400 and `{"error": "<field> is required"}`

### Requirement: Backend exposes a token verification endpoint
The system SHALL expose a `POST /api/verify` endpoint that accepts a token and returns the associated username if valid.

#### Scenario: Verify with valid token
- **WHEN** the client sends `POST /api/verify` with `{"token": "<valid-uuid>"}`
- **THEN** the server responds with HTTP 200 and `{"username": "admin"}`

#### Scenario: Verify with invalid or missing token
- **WHEN** the client sends `POST /api/verify` with an invalid or non-existent token
- **THEN** the server responds with HTTP 401 and `{"error": "Invalid token"}`

### Requirement: Backend exposes a logout endpoint
The system SHALL expose a `POST /api/logout` endpoint that clears the server-side session token.

#### Scenario: Successful logout
- **WHEN** the client sends `POST /api/logout` with `{"token": "<valid-uuid>"}`
- **THEN** the server clears the token from the user record and responds with HTTP 200

#### Scenario: Logout with invalid token
- **WHEN** the client sends `POST /api/logout` with an invalid token
- **THEN** the server responds with HTTP 400 and `{"error": "Invalid token"}`

### Requirement: SPA login view presents a login form and integrates with the API
The system SHALL serve `index.html` as a SPA shell. When the hash route is `#login` (or default), a login form with username and password fields is displayed. On successful login, the frontend stores the token and navigates to `#home`.

#### Scenario: User accesses the application
- **WHEN** the user navigates to the application root URL in a browser
- **THEN** the SPA loads, defaults to the `#login` route, and displays a login form with username and password fields

#### Scenario: Successful login via the SPA
- **WHEN** the user enters correct credentials and submits the form
- **THEN** the frontend calls `POST /api/login`, receives a token, stores it in `localStorage`, and navigates to `#home`

#### Scenario: Failed login via the SPA
- **WHEN** the user enters incorrect credentials and submits the form
- **THEN** the frontend calls `POST /api/login`, receives an error, and displays the error message on the `#login` view without navigating

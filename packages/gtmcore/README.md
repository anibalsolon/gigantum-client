# Gigantum Client core libraries

The packages here contain core functionality of the Gigantum Client. For example,
this includes activity monitoring, environment management, and project/dataset
definitions.


## Packages

### configuration

A class for centralized configuration information is available via `gtmcore.configuration.Configuration`

The class loads configuration information found in a configuration file in this order:

1. Explicitly passed into the constructor
2. A file in the "installed" locations (`/etc/gigantum/labmanager.yaml`)
3. The default file in the package (`/configuration/config/labmanager.yaml.default`)

The configuration file is YAML based and should be used for all parameter
storage. Parameters should be broken into sections based on the component.

### logging

A pre-configured logger is available from the class from
gtmcore.logging.LMLogger.

It loads logger configuration from a configuration json file in this order:

1. Explicity passed into the constructor
2. A file in the "installed" locations (`/etc/gigantum/logging.json`)
3. The default file in the package (`/logging/logging.json.default`)

If the default file is loaded, it is assumed that the log file location will
not be available and a temporary file is automatically used.

The current configuration logs `INFO` messages and higher. If you wish to log
debug messages, you must set the log level to `DEBUG`. The python logger used
is named `labmanager`.

Example usage in Python code:

```
lmlog = LMLogger().logger

lmlog.info("This is my info message")
lmlog.warning("This is my warning message")
lmlog.error("This is my error message")
```

### auth

The auth package provides user authentication tools and middleware to create
user identities from JSON Web Tokens (JWT) that come from auth0. To get all
tests to pass, you need to set the auth server info in
`gtmcore/auth/tests/auth_config.json`.  Ask a developer for this file.

To configure from scratch:

- In Auth0 create a new database connection that will hold your test user
- Add a test user to the connection with the following attributes:
    - username: johndoe
    - given_name: John
    - family_name: Doe
    - email: john.doe@gmail.com
- Create a new test API and client, configuring the client to only allow
  password grants
- Update API to use RSA
- Update `gtmcore/auth/tests/auth_config.json.example` to
  `gtmcore/auth/tests/auth_config.json`, setting all values

## Testing

Tests are written using pytest. To run unit tests, simply execute pytest

## Contributing

Gigantum uses the [Developer Certificate of Origin](https://developercertificate.org/). 
This is lightweight approach that doesn't require submission and review of a
separate contributor agreement.  Code is signed directly by the developer using
facilities built into git.

Please see [`docs/contributing.md`  in the gtm
repository](https://github.com/gigantum/gtm/tree/integration/docs/contributing.md).

## Credits

TODO

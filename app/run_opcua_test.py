import os

from app.opcua_test_app import create_opcua_test_app


app = create_opcua_test_app()


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=int(os.getenv("OPCUA_TEST_PORT", "5051")), debug=debug_mode)

import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.getenv("SESSION_SECRET", "dev_secret_key")
    APP_NAME = "Les Viviers de Noirmoutier"
    APP_SUBTITLE = "Supervision de production et maintenance"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "0") == "1"

    MYSQL_HOST = os.getenv("MYSQL_HOST", "db")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "les_viviers_de_noirmoutier")

    OPCUA_TEST_NODE_FILE = os.getenv(
        "OPCUA_TEST_NODE_FILE",
        os.path.join(BASE_DIR, "data", "opcua_test_nodes.txt"),
    )
    OPCUA_TEST_ENDPOINT = os.getenv("OPCUA_TEST_ENDPOINT", "opc.tcp://172.30.30.20:4840")
    OPCUA_TEST_USERNAME = os.getenv("OPCUA_TEST_USERNAME", "admin")
    OPCUA_TEST_PASSWORD = os.getenv("OPCUA_TEST_PASSWORD", "wago")
    OPCUA_TEST_TIMEOUT = float(os.getenv("OPCUA_TEST_TIMEOUT", "3"))
    OPCUA_TEST_PORT = int(os.getenv("OPCUA_TEST_PORT", "5051"))
    OPCUA_CONFIGURED_VARIABLE_CACHE_TTL = float(
        os.getenv("OPCUA_CONFIGURED_VARIABLE_CACHE_TTL", "15")
    )
    OPCUA_CONFIGURED_VARIABLE_ERROR_CACHE_TTL = float(
        os.getenv("OPCUA_CONFIGURED_VARIABLE_ERROR_CACHE_TTL", "10")
    )
    OPCUA_COMMAND_COUNTER_NODE_ID = os.getenv(
        "OPCUA_COMMAND_COUNTER_NODE_ID",
        "ns=4;s=|var|CC100-638A7C.Application.GVL_IHM.IHM_NB_Caisse",
    )
    OPCUA_COMMAND_COUNTER_LABEL = os.getenv(
        "OPCUA_COMMAND_COUNTER_LABEL",
        "Num caisse",
    )
    OPCUA_COMMAND_COUNTER_TIMEOUT = float(
        os.getenv("OPCUA_COMMAND_COUNTER_TIMEOUT", "8")
    )
    OPCUA_COMMAND_COUNTER_ATTEMPTS = int(
        os.getenv("OPCUA_COMMAND_COUNTER_ATTEMPTS", "3")
    )
    OPCUA_COMMAND_COUNTER_PRECHECK_TIMEOUT = float(
        os.getenv("OPCUA_COMMAND_COUNTER_PRECHECK_TIMEOUT", "0.5")
    )
    OPCUA_DASHBOARD_LINE_STATUS_NODE_ID = os.getenv(
        "OPCUA_DASHBOARD_LINE_STATUS_NODE_ID",
        "ns=4;s=|var|CC100-638A7C.Application.GVL_IHM.IHM_En_Prod",
    )
    OPCUA_DASHBOARD_LINE_STATUS_LABEL = os.getenv(
        "OPCUA_DASHBOARD_LINE_STATUS_LABEL",
        "Statut ligne",
    )
    OPCUA_DASHBOARD_LINE_STATUS_TIMEOUT = float(
        os.getenv("OPCUA_DASHBOARD_LINE_STATUS_TIMEOUT", "3")
    )
    OPCUA_DASHBOARD_LINE_STATUS_ATTEMPTS = int(
        os.getenv("OPCUA_DASHBOARD_LINE_STATUS_ATTEMPTS", "1")
    )
    OPCUA_DASHBOARD_LINE_STATUS_PRECHECK_TIMEOUT = float(
        os.getenv("OPCUA_DASHBOARD_LINE_STATUS_PRECHECK_TIMEOUT", "0.5")
    )
    OPCUA_CURRENT_ORDER_START_NODE_ID = os.getenv(
        "OPCUA_CURRENT_ORDER_START_NODE_ID",
        "ns=4;s=|var|CC100-638A7C.Application.G7_PROD.stCurrentOrder.sDateDebut",
    )
    OPCUA_CURRENT_ORDER_END_NODE_ID = os.getenv(
        "OPCUA_CURRENT_ORDER_END_NODE_ID",
        "ns=4;s=|var|CC100-638A7C.Application.G7_PROD.stCurrentOrder.sDateFin",
    )
    OPCUA_CURRENT_ORDER_DURATION_NODE_ID = os.getenv(
        "OPCUA_CURRENT_ORDER_DURATION_NODE_ID",
        "ns=4;s=|var|CC100-638A7C.Application.G7_PROD.stCurrentOrder.tTempsProd",
    )
    OPCUA_CURRENT_ORDER_REQUESTED_BOXES_NODE_ID = os.getenv(
        "OPCUA_CURRENT_ORDER_REQUESTED_BOXES_NODE_ID",
        "ns=4;s=|var|CC100-638A7C.Application.G7_PROD.stCurrentOrder.iCaisseDemande",
    )
    OPCUA_CURRENT_ORDER_PRODUCED_BOXES_NODE_ID = os.getenv(
        "OPCUA_CURRENT_ORDER_PRODUCED_BOXES_NODE_ID",
        "ns=4;s=|var|CC100-638A7C.Application.G7_PROD.stCurrentOrder.iCaisseProduite",
    )
    OPCUA_CURRENT_ORDER_TIMEOUT = float(
        os.getenv("OPCUA_CURRENT_ORDER_TIMEOUT", "3")
    )
    OPCUA_CURRENT_ORDER_ATTEMPTS = int(
        os.getenv("OPCUA_CURRENT_ORDER_ATTEMPTS", "1")
    )
    OPCUA_CURRENT_ORDER_PRECHECK_TIMEOUT = float(
        os.getenv("OPCUA_CURRENT_ORDER_PRECHECK_TIMEOUT", "0.5")
    )

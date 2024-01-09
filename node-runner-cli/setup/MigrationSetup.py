from utils.Prompts import Prompts


class MigrationSetup:
    @staticmethod
    def ask_migration_config(
        current_config,
        olympia_node_url,
        olympia_node_auth_user,
        olympia_node_auth_password,
        olympia_node_bech32_address,
    ):
        new_config = current_config
        new_config.migration.use_olympia = True

        # Moved to default values
        # new_config.core_node.memory_limit: str = "14000m"
        # new_config.core_node.java_opts = "--enable-preview -server -Xms12g -Xmx12g  " \
        #                                  "-XX:MaxDirectMemorySize=2048m " \
        #                                  "-XX:+HeapDumpOnOutOfMemoryError -XX:+UseCompressedOops " \
        #                                  "-Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts " \
        #                                  "-Djavax.net.ssl.trustStoreType=jks -Djava.security.egd=file:/dev/urandom " \
        #                                  "-DLog4jContextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector"
        if olympia_node_url is None:
            olympia_node_url = Prompts.ask_olympia_node_url()
        new_config.migration.olympia_node_url = olympia_node_url

        if olympia_node_bech32_address is None:
            olympia_node_bech32_address = Prompts.ask_olympia_node_bech32_address()
        new_config.migration.olympia_node_bech32_address = olympia_node_bech32_address

        if olympia_node_auth_user is None:
            olympia_node_auth_user = Prompts.ask_olympia_node_auth_user()
        new_config.migration.olympia_node_auth_user = olympia_node_auth_user

        if olympia_node_auth_password is None:
            olympia_node_auth_password = Prompts.ask_olympia_node_auth_password()
        new_config.migration.olympia_node_auth_password = olympia_node_auth_password
        return new_config

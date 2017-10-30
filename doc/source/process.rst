###############
Tep Base Daemon
###############

Global Overiew
##############

.. mermaid::

    sequenceDiagram

        participant TepDaemon
        participant Initializer
        participant SubTasker

        activate TepDaemon
            TepDaemon ->> TepDaemon: Create Logger
            TepDaemon ->> TepDaemon: Create WampClient
            TepDaemon ->> TepDaemon: Create EtcdWrapper

            TepDaemon ->> Initializer: Create Initializer object
            Initializer -->> TepDaemon: Initializer object created
            TepDaemon ->> SubTasker: Create Subtasker object
            SubTasker -->> TepDaemon: Subtasker object created

            TepDaemon ->> TepDaemon: Create DialogsHandler
            TepDaemon ->> TepDaemon: Create MemoryHandler
            TepDaemon ->> TepDaemon: Create IntentsHandler
            TepDaemon ->> TepDaemon: Create SettingsHandler
            TepDaemon ->> TepDaemon: Create RegistryHandler

            TepDaemon ->> Initializer: Start Initializer
            activate Initializer
                Initializer ->> Initializer: Start WampClient
                Initializer ->> Initializer: Load dialogs
                Initializer ->> Initializer: Read setings
                Initializer ->> Initializer: Load Intents
                Initializer ->> SubTasker: Start SubTasker
                activate SubTasker
                    SubTasker ->> SubTasker: Start Settings listener
                    SubTasker -->> Initializer: SubTasker started
                deactivate SubTasker
                Initializer -->> TepDaemon: Initializer started
            deactivate Initializer
            TepDaemon ->> TepDaemon: Main Loop
        deactivate TepDaemon

--------

Summary
#######

.. mermaid::

    sequenceDiagram

        participant TepDaemon
        participant Initializer
        participant SubTasker

        activate TepDaemon
            TepDaemon ->> TepDaemon: Create TepDaemon
            TepDaemon ->> TepDaemon: Run TepDaemon Initializer
            TepDaemon ->> TepDaemon: Run TepDaemon Main Loop
            TepDaemon ->> TepDaemon: TepDaemon Shutdown
        deactivate TepDaemon

--------


Detailed
########

TepDaemon creation
==================

.. automodule:: tuxeatpi_common.initializer

    .. autoclass:: Initializer
        :noindex:

        .. automethod:: __init__
            :noindex:


.. mermaid::

    sequenceDiagram

        participant TepDaemon
        participant Initializer
        participant WampClient
        participant EtcdClient
        participant SubTasker

        activate TepDaemon
            TepDaemon ->> TepDaemon: Create logger

            TepDaemon ->> WampClient: Create instance
            activate WampClient
                WampClient -->> TepDaemon: Return instance
            deactivate WampClient

            TepDaemon ->> EtcdClient: Create instance
            activate EtcdClient
                EtcdClient -->> TepDaemon: Return instance
            deactivate EtcdClient

            TepDaemon ->> Initializer: Create instance
            activate Initializer
                Initializer -->> TepDaemon: Return instance
            deactivate Initializer

            TepDaemon ->> SubTasker: Create instance
            activate SubTasker
                SubTasker -->> TepDaemon: Return instance
            deactivate SubTasker

            TepDaemon ->> DialogsHandler: Create instance
            activate DialogsHandler
                DialogsHandler -->> TepDaemon: Return instance
            deactivate DialogsHandler

            TepDaemon ->> MemoryHandler: Create instance
            activate MemoryHandler
                MemoryHandler -->> TepDaemon: Return instance
            deactivate MemoryHandler

            TepDaemon ->> IntentHandler: Create instance
            activate IntentHandler
                IntentHandler -->> TepDaemon: Return instance
            deactivate IntentHandler

            TepDaemon ->> SettingsHandler: Create instance
            activate SettingsHandler
                SettingsHandler -->> TepDaemon: Return instance
            deactivate SettingsHandler 

            TepDaemon ->> RegistryHandler: Create instance
            activate RegistryHandler
                RegistryHandler -->> TepDaemon: Return instance
            deactivate RegistryHandler
        deactivate TepDaemon

--------

Initializer
===========

.. automodule:: tuxeatpi_common.initializer

    .. autoclass:: Initializer
        :noindex:

        .. automethod:: run
            :noindex:

.. mermaid::

    sequenceDiagram

        participant TepDaemon
        participant Initializer
        participant WampClient
        participant EtcdClient
        participant SubTasker

        activate TepDaemon
            TepDaemon ->> Initializer: Run
            activate Initializer

                Initializer ->> WampClient: Start
                activate WampClient
                    WampClient ->> WampClient: Connected
                    WampClient -->> Initializer: Started
                deactivate WampClient

                Initializer ->> DialogsHandler: Load dialogs
                activate DialogsHandler
                    DialogsHandler ->> DialogsHandler: Read dialogs files
                    DialogsHandler -->> Initializer: Dialogs loaded
                deactivate DialogsHandler

                Initializer ->> SettingsHandler: Load Settings
                activate SettingsHandler
                    SettingsHandler ->> SettingsHandler: Read component settings from Etcd
                    SettingsHandler ->> SettingsHandler: Read global settings from Etcd
                    SettingsHandler -->> Initializer: Settings loaded
                deactivate SettingsHandler

                Initializer ->> IntentHandler: Push intents
                activate IntentHandler
                    IntentHandler ->> IntentHandler: Read intents
                    IntentHandler ->> IntentHandler: Push intents to Etcd
                    IntentHandler -->> Initializer: Intents loaded
                deactivate IntentHandler


                Initializer ->> SubTasker: Start subtasker
                activate SubTasker
                    SubTasker ->> SettingsHandler: Start listener
                    activate SettingsHandler
                        loop Background asyncio loop
                            SettingsHandler ->> SettingsHandler: Listen for component settings changes
                            SettingsHandler ->> SettingsHandler: Listen for global settings changes
                        end
                        SettingsHandler -->> SubTasker: Listener started
                    deactivate SettingsHandler
                    SubTasker -->> Initializer: Subtasker started
                deactivate SubTasker

                Initializer -->> TepDaemon: initialization completed
            deactivate Initializer
        deactivate TepDaemon

--------

Main Loop
=========

.. automodule:: tuxeatpi_common.daemon

    .. autoclass:: TepBaseDaemon
        :noindex:

        .. automethod:: main_loop
            :noindex:

.. mermaid::

    sequenceDiagram

        participant TepDaemon

        activate TepDaemon
            loop Mainloop
                TepDaemon ->> TepDaemon: sleep(1)
            end
        deactivate TepDaemon


--------

Shutdown
========

.. automodule:: tuxeatpi_common.daemon

    .. autoclass:: TepBaseDaemon
        :noindex:

        .. automethod:: shutdown
            :noindex:



.. mermaid::

    sequenceDiagram

        participant TepDaemon
        participant SubTasker
        participant WampClient

        activate TepDaemon
            TepDaemon ->> TepDaemon: Stop settings

            TepDaemon ->> SubTasker: Stop
            activate SubTasker
                SubTasker -->> TepDaemon: Stopped
            deactivate SubTasker

            TepDaemon ->> WampClient: Stop
            activate WampClient
                WampClient -->> TepDaemon: Stopped
            deactivate WampClient

            TepDaemon ->> TepDaemon: Stop mainloop
        deactivate TepDaemon

APPLICATION = luke_dino

BOARD ?= samr21-xpro

SERIAL ?= ATML2127031800001935

RIOTBASE ?= $(CURDIR)/../RIOT

EXTERNAL_MODULE_DIRS += ../common

FEATURE_REQUIRED += periph_gpio

USEMODULE += gnrc_netdev_default
USEMODULE += auto_init_gnrc_netif
USEMODULE += cord_ep
USEMODULE += gcoap
USEMODULE += gnrc_icmpv6_echo
USEMODULE += gnrc_ipv6_default
USEMODULE += luke_common

DEVELHELP       ?= 0
DEFAULT_CHANNEL ?= 19
DINO_MOVE_PIN   ?= GPIO_PIN(PB, 2)

CFLAGS += "-DDINO_MOVE_PIN=$(DINO_MOVE_PIN)"
CFLAGS += -DIEEE802154_DEFAULT_CHANNEL=$(DEFAULT_CHANNEL)
CFLAGS += -DGNRC_IPV6_NIB_CONF_SLAAC=1

INCLUDES = -I$(CURDIR)/../common/

include $(RIOTBASE)/Makefile.include



MY_LIBRARIES := oscpack

CC := g++
FILES := main.c
CFLAGS=-Wall -pedantic -g 
LIBS += $(foreach library, $(MY_LIBRARIES), -L/usr/lib/lib$(library).so)
LINKS := $(foreach library, $(MY_LIBRARIES), -l$(library))
INCLUDES := -I/usr/include/


all:
	@echo $(LINKS)
	$(CC) $(CFLAGS) $(LIBS) $(INCLUDES) -o mouseblaster $(FILES) $(LINKS)
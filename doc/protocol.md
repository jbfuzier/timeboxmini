# Protocol documentation
This document is based on information from GitHb users [derHeinz](https://github.com/derHeinz/divoom-adapter) and [ScR4tCh](https://github.com/ScR4tCh/timebox).
It is a draft documentation of the protocol used to interact with the Divoom Timebox. It is far from complete.

## setting up a connection
Communication to the Timebox is established by opening a bluetooth socket on port 4 of the Timebox.
Serial data is exchanged as sequences of bytes. We will use hexadecimal notation for the data in this document. After opening the connection, the Timebox will initially respond with the 
byte sequence `00 05 48 45 4C 4C 4F 00` (which spells 'HELLO'). This byte sequence deviates from the structure of the subsequent communications.

## message structure
From the client to the Timebox and vice versa, data is exchanged in the form of *messages* with a particular format.
* A message always starts with the byte 0x01.
* A message always ends with the byte 0x02.
* Inside a message the bytes 0x01 and 0x02 are not used.
* To be able to communicate also the values 0x01 and 0x02, *masking* (or *escaping*) is used as follows. Whenever the original data includes one of the bytes 0x01, 0x02 or 0x03, then this byte
  is replaced by two bytes: 0x03, followed by 0x04, 0x05 or 0x06 respectively (the original values plus 3).
* After removal of the 0x01 head and 0x02 tail and unmasking the data, we obtain the message *payload*, followed, at the end, by a two-byte checksum.
* The checksum is computed by adding up all the bytes of the payload. This number is then represented with its least-significant byte (lowest 8 bits) first and most-significat byte (highest 8 bits) second.

## command structure
* The message payload obeys the following structure. We will call them *commands*.
* All commands (both to and from the Timebox) start with the command length, coded in two bytes, again LSB first. For example, in the command to view the clock: `05 00 45 00 01`, the initial bytes 05 00 indicate the command length (5).
  (I am assuming that the length is coded in two bytes. I have not seen a command yet longer than 255 bytes. Hence I have never observed a value different from 0 for the second byte of a command.) Note that the full *message* corresponding to this command, including masking, checksum and end markers is: `01 05 00 45 00 03 04 4B 00 02`.
* The command length is followed by one byte indicating the actual command type (0x45, 'switch view' in the example)
* The remainder of the command depends on the command type (00=clock, 01=24h in the example) and sometimes has optional extensions (such as specifying the color of the clock)
* The responses from the Timebox to the client have a similar structure. They start with the two byte command length. The third byte has as far as I have observed always the value 0x04. The fourth byte is the command number. The fifth byte seems always 0x55, command dependent data follows after the fifth byte, if any.
* Responses are typically returned after commands to the Timebox with the same command, followed by 55, possibly followed by additional information. For instance, when some information was requested from the Timebox such as the current radio frequency. Or without additional information as an acknowledgement.
* The response to a malformed command is a negative acknowledgement of the form XX AA, where XX is the command number that was erroneous.
* The initial communication from the Timebox does not follow the usual structure. It is always 00 05 48 45 4C 4C 4F 00.

## command list
Some of the known commands:
* **0x05 Turn radio on/off**
  Followed by 0x00 = off, or 0x01 = on. For example. To turn the radion on send the command `04 00 05 01`.
* **0x08 Set volume**
  Followed by the volume between 0x00 and 0x10. To set the volume to level 3, send the command `04 00 08 03`
* **0x09 Get current volume**
  To request the current volume setting, send the command `03 00 09`. The Timebox will then respond with a command of the form `06 00 04 09 55 XX`, where `XX` is the current volume setting.
* **0x0a Set mute state**
  Followed by 0x00 = mute, or 0x01 = unmute.
* **0x0b Get mute state**
* **0x18 Set date and time**
  Followed by year (last two digits), year (first two digits), month, day, hours, minutes, seconds, and another number hundredths?
  The command is `0B 00 18 YY YY MM DD HH MM SS XX`
* **0x44 Set static image**
  This commands starts with `BD 00 44 00 0a 0a 04`, followed 182 bytes of image data. The image data includes 4 bits (a value between 0x0 and 0xf) for every color (R, G, B) for every pixel row by row from left to right and top to bottom.
  Two colors with 4 bits are combined into one byte, where the first color data occupies the lowest four bits and the second the highest four bits.
  This leads to 11x11x3 / 2, rounded up, equals 182 bytes of data.
* **0x45 Set view**
  Different views can be activated, clock, temperature, animations. 
  `05 00 45 01 00` shows the temperature in degrees Celsius. 
  `05 00 45 01 01` shows the temperature in degrees Fahrenheit.
  Color information can be added:
  `08 00 45 01 00 RR GG BB` shows the temperature in the color specified in the last three bytes.
  `05 00 45 00 XX` shows the clock. `XX=00` in 12h and `XX=01` in 24h format. Color information can be added.
  `05 00 45 06 00` shows the stopwatch.
  `05 00 45 07 00` shows the score board.
* **0x49 Set image in an animation**
  Sets one frame as part of an animation. 
  This commands starts with `BF 00 49 00 0a 0a 04 NN TT`, where `NN` is the frame numbe and `TT` is the time delay in the animation. The encoding of the frame image is identical to the static image.
* **0x59 Get temperature**
  When the temperature changes the Timebox sends 0x59 messages on its own initiative.
* **0x60 Get current radio frequency**
  Returns two bytes `XX YY`, which represent the frequency YX.X MHz, for instance, `03 0A` represents 100.3Mhz.
* **0x61 Set radio frequency**
  Uses the same encoding of the frequency.

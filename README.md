# OctoPrint-IFTTT

Connects OctoPrint events to IFTTT.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/tjjfvi/OctoPrint-IFTTT/archive/master.zip

## Configuration

### Makerkeys
A unique API key for IFTTT. Go [here](https://ifttt.com/services/maker_webhooks/settings) and look for the URL. The last part (after the `/use/`) is the makerkey. You can put multiple makerkeys, seperated by newlines, here.

### Default prefixes
Default prefixes for the triggers. If you have an event `MyEvent` and prefixes `prefix1-` and `prefix2-`, it will, by default make the triggers `prefix1-MyEvent` and `prefix2-MyEvent`. Seperate the prefixes with newlines.

### Events
Define events to send to IFTTT.

#### Triggers
A list of triggers to trigger on IFTTT.

#### Values
IFTTT Webhooks allows for a payload with three values. It will interpret this string like so:
 - If the value begins with a dot (`.`), it will use that prop of the event payload (e.g. `.name` for `PrintDone`)
 - If it begins with a colon (`:`) it will use the string after the colon
 - Otherwise it will just send the plain text

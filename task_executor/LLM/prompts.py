keyboard_text = """As the keyboard is now awaken, you can call this function."""
keyboard_other = """Before calling this function, you must close the keyboard first."""
keyboard_back = """This function is used to close the keyboard."""

nokeyboard_text = """As the keyboard has not been awakened now, you cannot call this function. \
Before calling it, you should tap on a certain element to wake the keyboard up first."""
nokeyboard_back = """This function is used to return to the previous screen interface."""

plan_example = """APP: Call
task: Call the contact "Alice".
actions: 1.Tap on text "Contacts". 2.Tap on EditText box "Search contacts". 3.Enter text "Alice". 4.Tap \
the first item in the list. 5.Tap on Icon "call". 6.FINISH."""

task_template_img = """You are an agent that is trained to complete certain tasks on a smartphone. \
You will be given a task, a smartphone screenshot and the corresponding description in HTML-like format. \
You need to plan the next action to proceed with the task, and call the correct function to execute your \
plan. In the screen description, each UI element is labeled with a numeric tag "id" starting from 1. \
The IDs of non-textual elements have been marked on the image.

The function you can call to execute the action are as follows:

1. tap(element: int)
This function is used to tap an UI element on the screen. "element" is the numeric tag \
assigned to the UI element on the screen discription. <keyboard_other>
A simple use case can be tap(5), which taps the UI element labeled with the number 5.

2. long_press(element: int)
This function is used to long press an UI element on the screen. "element" is the numeric tag \
assigned to the UI element on the screen discription. <keyboard_other>
A simple use case can be long_press(2), which long presses the UI element labeled with the number 2.

3. scroll(direction: str)
This function is used to scroll the screen up or down. "direction" is the string of the direction you \
want the screen to scroll. Its value can be "up" or "down". "direction" must be wrapped with double quotation marks. \
<keyboard_other>
A simple use case can be scroll("down"), which is used to view elements that are not displayed below the \
current screen.

4. text(text_input: str)
This function is used to insert text input in an input field/box. "text_input" is the string you want to \
insert and must be wrapped with double quotation marks. <keyboard_text>
A simple use case can be text("Hello!"), which inserts the string "Hello!" into the input area \
on the smartphone screen.

5. back()
<keyboard_back> It has no parameters.

The APP you need to operate is: <APP_name>
The task you need to complete is: <task_description>
Your previous actions are summarized as follows: <last_acts>
<error_report>

The current screen description is as follows:

<screen_description>

Now, given the current screen description, you need to plan the next action and call the \
function to proceed with the task. Your output should include three parts in the given format:

Observation: <Briefly summarize the composition and functions of this screen.>
Thought: <To complete the given task, what is the next step you should do.>
Action: <Express your action decision in one sentence.>
Function: <The function you choose to call with the correct parameters to proceed with the task. \
If you believe the task is completed or there is nothing to be done, you should output FINISH. \
You cannot output anything else except a function call or FINISH in this field.>

You can only take one action at a time, so please directly call the function.
"""

task_template = """You are an agent that is trained to complete certain tasks on a smartphone. \
Given a task and a smartphone screen description in HTML-like format, you need to plan the next \
action to proceed with the task, and call the correct function to execute your plan. In the screen \
description, each UI element is labeled with a numeric tag "id" starting from 1. 

The function you can call to execute the action are as follows:

1. tap(element: int)
This function is used to tap an UI element on the screen. "element" is the numeric tag \
assigned to the UI element on the screen discription. <keyboard_other>
A simple use case can be tap(5), which taps the UI element labeled with the number 5.

2. long_press(element: int)
This function is used to long press an UI element on the screen. "element" is the numeric tag \
assigned to the UI element on the screen discription. <keyboard_other>
A simple use case can be long_press(2), which long presses the UI element labeled with the number 2.

3. scroll(direction: str)
This function is used to scroll the screen up or down. "direction" is the string of the direction you \
want the screen to scroll. Its value can be "up" or "down". "direction" must be wrapped with double quotation marks. \
<keyboard_other>
A simple use case can be scroll("down"), which is used to view elements that are not displayed below the \
current screen.

4. text(text_input: str)
This function is used to insert text input in an input field/box. "text_input" is the string you want to \
insert and must be wrapped with double quotation marks. <keyboard_text>
A simple use case can be text("Hello!"), which inserts the string "Hello!" into the input area \
on the smartphone screen.

5. back()
<keyboard_back> It has no parameters.

The APP you need to operate is: <APP_name>
The task you need to complete is: <task_description>
Your previous actions are summarized as follows: <last_acts>
<error_report>

The current screen description is as follows:

<screen_description>

Now, given the current screen description, you need to plan the next action and call the \
function to proceed with the task. Your output should include three parts in the given format:

Observation: <Briefly summarize the composition and functions of this screen.>
Thought: <To complete the given task, what is the next step you should do.>
Action: <Express your action decision in one sentence.>
Function: <The function you choose to call with the correct parameters to proceed with the task. \
If you believe the task is completed or there is nothing to be done, you should output FINISH. \
You cannot output anything else except a function call or FINISH in this field.>

You can only take one action at a time, so please directly call the function.
"""

data_generate_prompt = """You need to create a task set for an smartphone operating agent. \
You will be given a GUI screenshot and the corresponding description in HTML-like format. \
In the screen description, each UI element is labeled with a numeric tag "id" starting from 1. \
The IDs of non-textual elements have been marked on the image.

The smartphone operating agent can call functions as follows:

1. tap(element: int)
This function is used to tap an UI element on the screen. "element" is the numeric tag \
assigned to the UI element on the screen discription. <keyboard_other>
A simple use case can be tap(5), which taps the UI element labeled with the number 5.

2. long_press(element: int)
This function is used to long press an UI element on the screen. "element" is the numeric tag \
assigned to the UI element on the screen discription. <keyboard_other>
A simple use case can be long_press(2), which long presses the UI element labeled with the number 2.

3. scroll(direction: str)
This function is used to scroll the screen up or down. "direction" is the string of the direction you \
want the screen to scroll. Its value can be "up" or "down". "direction" must be wrapped with double quotation marks. \
<keyboard_other>
A simple use case can be scroll("down"), which is used to view elements that are not displayed below the \
current screen.

4. text(text_input: str)
This function is used to insert text input in an input field/box. "text_input" is the string you want to \
insert and must be wrapped with double quotation marks. <keyboard_text>
A simple use case can be text("Hello!"), which inserts the string "Hello!" into the input area \
on the smartphone screen.

The screen description is as follows:

<screen_description>

Now, given the screen description, you need to provide some tasks that can be completed using \
a single function call on the current GUI interface. To ensure difficulty, the task description \
should not be too simple and clear, and should strive to conform to human natural language rather than \
machine instructions. Each task should be described in the following format:

Task: <Provide a task description in one sentence.>
Function: <The functions that need to be called to complete this task. You cannot output anything else except a function call>

Here is an example:

Task: Find a news article about France for me.
Function: text("France")
"""
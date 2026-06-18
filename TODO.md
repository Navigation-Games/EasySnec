This is a todo list! Should it live in the github issues page? Probly, but I'm lazy.


Things to do before live demo tomorrow:


- [ ] nice to have: emoji or image mappings for mistake display
- [ ] nice to have: more faces


- [x] nice to have: welcome state on the running window
- [x] sound (via python)
- [x] fix image backgrounds
- [x] ensure the courses+animal mappings are correct
- [x] threads work w/o mock stuff
- [x] display results
    - [x] show missing checkpoints
    - [x] show missed start/finish
      - [x] show specific face for this
    - [x] show time
    - [x] show face
- [x] update mistakes to show index instead
- [x] calculate mistakes - for animal-O scoring mode specifically
    - [x] make sure the ordering is correct
- [x] course dropdown
- [x] return to setup button

- [x] Do backend<>frontend data exchange via a "Model" or "Object." This will be more efficient and more structured
- [x] Do backend<>frontend event exchange via QT slots
- [x] Make a functioning and beautiful port selection page
- [x] Logic - score-o and classic-o
- [x] Make clever score representation for classic-o
- [x] Implement typeguard (note - this will only guard function calls. It does no checking whatsoever on dataclasses)

- [ ] Course upload backend
- [ ] Course upload frontend
- [ ] guess if student forgot about order?
    - say "5/5, but out of order!"
    - maybe just if only swap errors
- [x] feedback screen needs a dropdown to change course

- [ ] implement a color scheme. no pallete business, just some globals
- [ ] make the left and right headers equal size


What do I need to do before this slint version becomes deployable?
- [x] issue: changing port list resets the current selection
- [x] make a mock si player. it should be graphical!
    - [x] either use slint to make an entirely new window+process, or make a popup window or smth.


Erkan's EasyGecNG Notes
- there's no icon
- the terminal is annoying
- have animal-O be the default or built in
    - ideally this would be a set of pins that you could edit
        - how does state work? Dev team could make defaults and users could modify the list
        - We could pull courses from the website

- adding stations when building courses is really annoying. make it better
- don't ask to save current event
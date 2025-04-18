on run {input, parameters}
	tell application "System Settings"
		activate
	end tell
	tell application "System Events"
		tell application process "System Settings"
			tell splitter group 1 of group 1 of window 1
				tell group 2 to tell group 1 to tell scroll area 1 to tell group 3
					repeat until UI element 1 exists
						delay 1
					end repeat
					click UI element 1
					repeat until UI element 2 exists
						delay 1
					end repeat
					click UI element 2
				end tell
			end tell
			repeat until group 1 of group 1 of UI element 1 of scroll area 1 of sheet 1 of window 1 exists
				delay 1
			end repeat
			tell window 1 to tell sheet 1 to tell scroll area 1 to tell UI element 1
				tell group 1 of group 1
					click UI element 4 of group 1
					repeat until text field 1 of group 4 exists
						delay 0
					end repeat
					click text field 1 of group 4
					set value of text field 1 of group 4 to input
				end tell
				tell group 1 to tell group 2 to tell group 1
					repeat until UI element "Continue" of group 2 exists
						delay 1
					end repeat
					click UI element "Continue" of group 2
					repeat until UI element "Copy address" of group 1 exists
						delay 1
					end repeat
					click UI element "Copy address" of group 1
					repeat until UI element "Done" of group 2 exists
						delay 0
					end repeat
					click UI element "Done" of group 2
					repeat until UI element "Done" of group 1 exists
						delay 0
					end repeat
					click UI element "Done" of group 1
				end tell
			end tell
		end tell
	end tell
	return input
end run
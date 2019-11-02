import os
import sys
import time
import sqlite3
import urllib.request as req

def print_menu():
	print ("\n1 - Start workflow")
	print ("2 - Create new workflow")
	print ("3 - Edit workflow")
	print ("4 - Delete workflow")
	print ("5 - Print workflows")
	print ("6 - Exit")

def print_menu2():
	print ("\n\t1 - Change workflow name")
	print ("\t2 - Add path or URL")
	print ("\t3 - Delete Path or URL")
	print ("\t4 - Exit Edit")

def workflow_exists(data_base, workflow_name):
	result = False
	
	for path in data_base.execute("SELECT path FROM workflows WHERE workflow_name = ?;", (workflow_name,)):
		result = True
	
	return result

def path_exists(data_base, workflow_name, path):
	result = False
	
	for workflow_name, path in data_base.execute("SELECT workflow_name, path FROM workflows WHERE workflow_name = " + "'" + workflow_name + "'" + " and path = " + "'" + path + "';"):
		result = True
	
	return result

def url_is_valid(url):
	try:
		request = req.Request(url)
		try:
			site = req.urlopen(request)
			response = True
		except:
			response = False
	except:
		response = False
	
	return response

def get_paths_list(data_base, workflow_name):
	paths_list = []
	
	for path in data_base.execute("SELECT path FROM workflows WHERE workflow_name=?;",(workflow_name,)):
		paths_list.append(path[0])
	
	return paths_list

def main():
	connection = sqlite3.connect('workflows.db')
	data_base = connection.cursor()
	
	try:
		data_base.execute("CREATE TABLE workflows(workflow_name text, path text);")
	except Exception:
		pass
	
	run = True
	
	while run:
		print_menu()
		menu_choose = str(input("Enter your choice: "))
		
		if menu_choose is "1":
			workflow_name = str(input("Which workflow do you want to start? "))
			is_workflow_exist = False
			
			# iterate through each path 
			for path in data_base.execute("SELECT path FROM workflows WHERE workflow_name = " + "'" + workflow_name + "';"):
				try:
					# Start the path
					os.startfile(path[0])
					time.sleep(0.1)
				except Exception:
					print ("Error opening file: " + str(path[0]))
				# There is at least one path				
				is_workflow_exist = True
				
			if not is_workflow_exist:
				print ("This workflow does not exist...")
			else:
				print ("Enjoy")
				run = False
		
		elif menu_choose is "2":
			valid_path = []
			workflow_name = str(input("Enter a name for this workflow: "))
			
			if workflow_exists(data_base, workflow_name):
				print ("There's already a workflow with this name!")
			elif workflow_name == '':
				print ("Empty name?")
			else:
				print ("Enter the paths or URLs of your desired things to be open. Enter -1 to close and save this workflow")
				print ('')
				
				path = ""
				counter = 1
				
				while path != "-1":
					path = str(input("Enter path/URL number " + str(counter) + ": "))
					
					if (not os.path.exists(path) and not url_is_valid(path)) or path_exists(data_base, workflow_name, path):
						if path != "-1":
							print ("Path/URL either already exists or is invalid!")
						valid_path.append(False)
					else:
						values = (workflow_name, path)
						data_base.execute("INSERT INTO workflows VALUES (?,?);", values)
						print ("Path/URL saved")
						valid_path.append(True)
					counter += 1
				
				connection.commit()
				
				if True in valid_path:
					print (workflow_name + " workflow saved successfully!")
				else:
					print ("Workflow wasn't saved")
		
		elif menu_choose is "3":
			run2 = True
			workflow_name = str(input("Which workflow do you want to edit? "))
			
			if workflow_exists(data_base, workflow_name):
				while run2:
					print_menu2()
					edit_choose = str(input("\tEnter your choice: "))
					
					if edit_choose is "1":
						new_workflow_name = str(input("\tEnter new workflow name: "))
						data_base.execute("UPDATE workflows SET workflow_name = " + "'" + new_workflow_name + "'" + " WHERE workflow_name = " + "'" + workflow_name + "';")
						connection.commit()
						workflow_name = new_workflow_name
						print ("\tName changed!")
					elif edit_choose is "2":
						path = str(input("\tEnter the path/URL of your desired thing to be open: "))
						
						if (os.path.exists(path) or url_is_valid(path)) and not path_exists(data_base, workflow_name, path):
							values = (workflow_name, path)
							data_base.execute("INSERT INTO workflows VALUES (?,?);", values)
							connection.commit()
							print ("\tPath/URL added!")
						else:
							print ("\tPath/URL either already exists or is invalid!")
					elif edit_choose is "3":
						print ("\tEnter path/URL to delete:")
						print ('')
						
						paths_list = get_paths_list(data_base, workflow_name)
						paths_number_dict = {}
						
						for i in range(len(paths_list)):
							print("\t" + str(i + 1) + " - " + paths_list[i])
							paths_number_dict[str(i + 1)] = paths_list[i]
						
						path_number = str(input("\tEnter your choice: "))
						
						try:
							path = paths_number_dict[path_number]
						except:
							path = ""
						
						if path_exists(data_base, workflow_name, path):
							data_base.execute("DELETE FROM workflows WHERE workflow_name = " + "'" + workflow_name + "'" + " and path = " + "'" + path + "';")
							connection.commit()
							print ("\tPath/URL deleted!")
						else:
							print ("\tPath/URL doesn't exist!")
					elif edit_choose is "4":
						print ("\tChanges saved!")
						run2 = False
			else:
				print ("This workflow does not exist...")
		elif menu_choose is "4":
			workflow_name = str(input("Which workflow do you want to delete? "))
			
			# Check if the workflow exists
			if workflow_exists(data_base, workflow_name):
				data_base.execute("DELETE FROM workflows WHERE workflow_name = ?;", (workflow_name,))

				# Save changes to prevent loss
				connection.commit()
				print ("Workflow deleted successfully!")
			else:
				print ("This workflow does not exist...")
		
		elif menu_choose is "5":
			workflows_dict = {}
			
			for name in data_base.execute("SELECT workflow_name, path FROM workflows;"):
				workflows_dict[name[0]] = []
			
			for name in data_base.execute("SELECT workflow_name, path FROM workflows;"):
				workflows_dict[name[0]].append(name[1])
			
			if bool(workflows_dict):
				print ("We found these workflows:")
				print ('')
			else:
				print ("No workflows were created!")
			
			for key, value in workflows_dict.items():
				print ("Name: " + key)
				for i in range(len(value)):
					if i == 0:
						print ("Paths and URLs: " + value[i])
					else:
						print ("                " + value[i])
				print ('')
		
		elif menu_choose is "6":
			print ("See you later!")
			run = False
			
	# Save (commit) the changes
	connection.commit()
	connection.close()

if __name__ == "__main__": 
	main()
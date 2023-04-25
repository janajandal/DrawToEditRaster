#####
#Jana Jandal Alrifai
# 110069600
# ESCI 2721
# Dr. Cameron Proctor



#importations
import os, arcpy
import threading
from math import sqrt
from arcpy.sa import *
from pygame import *
from tkinter import *
import numpy as np


##setting up pygame window
size=width,height=1025,800 #sets width and height of the screen
screen = display.set_mode(size)  # displays the screen

#defining some basic colors
GREEN=(0, 193, 6)
RED = (178,34,34)
PURPLE=(226, 107, 255)
BLUE=(0, 0, 255)
BLACK=(0,0,0)
WHITE=(255,255,255)
LBLUE=(154, 219, 244)
colourList = [GREEN, RED, PURPLE, BLUE,BLACK, WHITE, LBLUE]
toolsList = ["point", "pencil", "brush", "rectangle", "circle"]

#initilize different modules
font.init()
root=Tk() #initialize tkinter windows
root.withdraw() #makes the window not visible
init() #initialize pygame
display.init() #intitalize the display portion of the pygame


#set up default values
color = BLACK
value = 0
tool = "point"


path = "C:\\Users\\janaj\\OneDrive\\Documents\\ArcGIS\\Projects\\MyProject1\\MyProject1.aprx" #hardcode the path so i can use this variable until the user inputs their preferred path
a = arcpy.env.workspace = "C:\\Users\\janaj\\OneDrive\\Documents\\ArcGIS\\Projects\\MyProject1" #hardcore the ArcGIS workspace


class UserMice:
    """represents the mouse attributes"""
    def __init__(self): #intitliazation functions
        self.sx, self.sy = 0,0  #start x, start y that help draw from the user WAS to where they will be
        self.th = 2 #thickness of the drawings
        self.pencilth = 1 #pencil thickness
        if self.th != 0:
            th2 = self.th #thickness 2 is used for the corners of rectangles to add a finished look to drawings
        mb = mouse.get_pressed()  # sees if mouse get pressed using pygame mouse from the python library
        self. mx, self.my = mouse.get_pos()  # gets mouses current position
        sx, sy = 0, 0  # start x, start y that help draw from the user WAS to where they will be
        self.omx = self.mx #original mouse x position is captured as the mouse clicks
        self.omy = self.my #original mouse y position is captured as the mouse clicks
        #omx and omy are utilised when the user is building a rectangle and the omx, omy represents the top left corner, the next time the user presses the mouse button, that mx,my becomes the new omx,omy
        mouse.set_cursor(cursors.arrow) #change the look of the mouse to a bigger arrow


MyMouse = UserMice() #make Mouse class objects

def runPygame():
    '''This function contains all the setup for pygame window and the pygame loop - this is done here in attempt to thread it
    and use it at a later time in the script so pygame and console inputs dont interfere with each other
    '''

    screen = display.set_mode(size)  # displays the screen
    clock = time.Clock() #Get the current processor time in seconds
    screenShot = screen.copy()


    #sets up the pygame loop
    done = False
    while not done:
        getEvent() #local function that checks mouse events, buttons held and any other user inputs
    display.flip()  #updates the entire frame
    clock.tick(60) #updates the frame display each 60 seconds

    quit() # Quit Pygame

def FindPixel():
    '''take a set of (x, y) coordinates which are the mouse coordinates we added to the list
    and converts them to row and column indices in the input raster.
    The row and column indices are then appended to a list and returned by the function.'''

    # get the extent from the input raster
    pixelWidth = inputRaster.extent.width #assign the width of the extent
    pixelHeight = inputRaster.extent.height #assign the height of the extent

    for coords in EditArea:
        mousex = coords[0] #get the x value from the couples coordinates in the list
        mousey = coords[1] #get the y value from the
        col_index = int(round((mousex - inputRaster.extent.XMin) / pixelWidth)) #calcuate the closest pixel to the mouse position by The formula takes into account the left edge of the raster and the width of each pixel and rounding it to match a colummn number in the raster
        row_index = int(round((inputRaster.extent.YMax - mousey) / pixelHeight)) #similiar to col_index but for the y coordinate and thus a row number
        closestPixel.append((col_index,row_index)) #append this to the cloest pixel list which will be iterated when editing the input raster

def RasterCellIterator():
    rasrow = int((arcpy.GetRasterProperties_management(inputRaster, "ROWCOUNT")).getOutput(0))  # use the built in method to get the row count values from the raster, and we only want the first part of the output, and we are manipulating it as an int
    rascol = int((arcpy.GetRasterProperties_management(inputRaster, "COLUMNCOUNT")).getOutput(0))  # very similiar to what we did in the above line, except it is about column counts
    EmptyArray = [[0] * rasrow for i in range(rascol)]  # make an empty array using a loop, the first part of the loop is multiplying the list by the row size, and we produce as many lists as there are columns

    for coordinates in closestPixel: #iterates through the closest pixels list
        row = coordinates[0] #gets the first part of the tuple - for the row
        col = coordinates[1] #gets the second part of the tuple - for the col
        EmptyArray[row][col] = value #access the row, column of the raster and change it to the value assigned to the colour the user is currently working on
    ArrayRaster = arcpy.NumPyArrayToRaster(np.array(EmptyArray), x_cell_size=inputRaster.meanCellHeight, y_cell_size=inputRaster.meanCellWidth,
                             lower_left_corner=inputRaster.lowerLeft)
def GetFirstRaster(ProjectPath):
    '''
    This is a function adapted from an assignment to iterate through a project
    and layers and return the first raster
    :param ProjectPath:
    :return r or None:
    '''
    try: #to ensure this does not stop
        pp = os.path.dirname(ProjectPath) #cuts the last part of the project path off so we have access to the fodler
        currentProject = arcpy.mp.ArcGISProject(ProjectPath) #established an ArcGIS project using arcpy mp
        currentMap = currentProject.listMaps("*")[0] #get all maps and get the first one
        for layer in currentMap.listLayers(): #iterate through the layers of the first map in the project
            if layer.isRasterLayer: #checks if the layer is a raster
                rasterPath = os.path.join(pp, layer.name) #returns path of the raster and joins the folder path to the raster name obtained
                if os.path.exists(rasterPath):  # Check if the file path exists
                    print(rasterPath)
                    r = Raster(in_raster=rasterPath) #makes the rasterpath a Raster object in python
                    return r
                else:
                    raise OSError(f"Could not locate file: {rasterPath}") #in case something went wrong, we ensure this does not crash
            else:
                print("there is no raster in the file")
        return None #if no raster, return none
    except Exception as e:
        print(f"Error: {str(e)}") #raise error if file could not be located
        return None

def NewRaster(pp, outputName, oldRaster): #this function will take either raster proorties or an old raster
    ShortPath = os.path.dirname(pp)
    extent = arcpy.Extent(oldRaster.extent.XMin, oldRaster.extent.YMin, oldRaster.extent.XMax, oldRaster.extent.YMax) #set the raster's extent
    cellSize = (oldRaster.meanCellHeight + oldRaster.meanCellWidth) / 2
    arcpy.CreateRasterDataset_management(ShortPath, outputName+ "_TIFF", cellSize , "32_BIT_FLOAT", oldRaster.spatialReference, 9) #use the built in raster maker
    return arcpy.Raster(outputName+"_TIFF")
inputRaster = Raster(GetFirstRaster(path)) #assign Raster object to input raster after getting the first raster using the function

if inputRaster.readOnly == True: #if the raster is read only, it cannot be edited, to avoid that, we make a copy
    copyName = input("this file is read only, type in a name for the working copy we will create") #asks the user to choose a name for the copy, otherwise we are not able to make a copy without repeating names
    inputRaster = NewRaster(path,copyName, inputRaster)#copies the raster with the same raster proprties which again assigned to the input raster variable
    HardCopyFail = True #if the user is not using input and hardcoding the path, they wont need to answer the future question
CircleRect=Rect(120,20,40,40) #used to normalize and make circles look better when drawn by the user

EditArea = [(18.4,3.4), (7.5,4.2)] #currently, we are not able to get information from the pygame window so I have hard coded some examples
closestPixel = [] #empty list that will be iterated through, this contains the most accurate versions of the pixels that will be used to access those pixels in the raster

rasrow = int((arcpy.GetRasterProperties_management(inputRaster, "ROWCOUNT")).getOutput(0)) #use the built in method to get the row count values from the raster, and we only want the first part of the output, and we are manipulating it as an int
rascol = int((arcpy.GetRasterProperties_management(inputRaster, "COLUMNCOUNT")).getOutput(0))

RasterGrid: rascol * rascol #figures out the grid dimensions


#these codeblocks figures out the user selected areas and adds those pixels to the EditArea list
def FindEditAreaRect(grid):
    '''
    :param grid: the grid is used because we are going to iterate through horizontally and vertically - the grid is the RasterGrid
    '''
    for i in range(MyMouse.sx, MyMouse.mx - MyMouse.sx): #loops through the mouse x position and the start x position
        for j in range(MyMouse.sy, MyMouse.my - MyMouse.sy): #looops through mouse y and start y position
            if i >= 0 and i < len(grid) and j >= 0 and j < len(grid[0]): #checks if that pixel is within the user selected areas
                EditArea.append(grid[i][j]) #append that pixel to the edit area list
def FindEditedAreaLine():
    ''''
    goes through the length of the line, even if it is horizontal or diagonal and append those pixels
    '''
    for i in range (MyMouse.omx - MyMouse.mx):
        for j in range (MyMouse.omy - MyMouse.my):
            EditArea.append(i,j)
def FindEditAreaCircle(radius, grid):
    '''
    :param grid: the grid is used because we are going to iterate through horizontally and vertically - the grid is the RasterGrid
    '''
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            # Calculate the distance between the center of the circle and the current cell
            dist = math.sqrt((i - MyMouse.sx) ** 2 + (j - MyMouse.sy) ** 2)
            if dist <= radius: #if the distance of the pixel is within the areas of the circle
                EditArea.append(grid[i][j])#append that pixel to the edit area list



def checkTool(screen):
    '''
    This function goes through and checks what tool is being used and runs the code for the tool, eventually it will call
    the related function to find the edit area
    :param screen:

    '''
    if tool == "pencil":
        draw.line(screen, color, (MyMouse.omx, MyMouse.omy), (MyMouse.mx, MyMouse.my))  # draws a line following the mouse
        FindEditedAreaLine()
    elif tool == "eraser":
        dx = MyMouse.mx - MyMouse.omx  # ditsnace between the current x position and original x position
        dy = MyMouse.my - MyMouse.omy  # ditsnace between the current y position and original y position
        dist = int(sqrt(dx ** 2 + dy ** 2))  # distance between 2 points formula
        if dist == 0:  # draw s circle if only one click is done
            draw.circle(screen, WHITE, (MyMouse.mx, MyMouse.my), MyMouse.th2)
        for i in range(1, dist + 1):  # draws a circle in between the gaps
            dotX = int(MyMouse.omx + i * dx / dist)
            dotY = int(MyMouse.omy + i * dy / dist)
            draw.circle(screen, WHITE, (dotX, dotY), MyMouse.th2)
    elif tool == "brush":
        #this tool produces a thicker line and thus it is important that no matter the speed the user is painting at, the line will not cut off
        distX = MyMouse.mx - MyMouse.omx #distance of x
        distY = MyMouse.my - MyMouse.omy #distance of y
        pythogoreanDist = int(sqrt(distX ** 2 + distY ** 2))
        if pythogoreanDist == 0: #if the mouse has not moved
            draw.circle(screen, color, (MyMouse.mx, MyMouse.my), MyMouse.th2 * 2) #draw a circle with the size of the thickness2
        for i in range(1, pythogoreanDist + 1):
            #the code loops through each pixel along the line connecting the previous mouse position (MyMouse.omx, MyMouse.omy) and the current mouse position (MyMouse.mx, MyMouse.my).
            #It calculates the x and y coordinates of each pixel along the line using linear interpolation, and draws a circle at that position with a radius of MyMouse.th2 * 2.
            dotX = int(MyMouse.omx + i * distX / pythogoreanDist)
            dotY = int(MyMouse.omy + i * distY / pythogoreanDist)
            draw.circle(screen, color, (dotX, dotY), MyMouse.th2 * 2)
        FindEditedAreaLine()
    elif tool == "circle":
        #calcualtes the hoirzontal and vertical distances so that we can draw diagonally
        radx = (MyMouse.mx - MyMouse.sx)
        rady = (MyMouse.my - MyMouse.sy)
        try:
            for i in range(6):  # improves the quality of the ellipse by drawing an ellipse with a given thickness with equal dimensions
                #draws four ellipses with the same dimensions as the first one, but with their centers shifted by a few pixels in each direction (up, down, left, right) from the starting point.
                ellDraw = Rect(MyMouse.sx + i, MyMouse.sy, radx, rady)
                draw.ellipse(screen, color, ellDraw, MyMouse.th)
                CircleRect.normalize()
                ellDraw = Rect(MyMouse.sx - i, MyMouse.sy, radx, rady)
                CircleRect.normalize()
                draw.ellipse(screen, color, ellDraw, MyMouse.th)
                ellDraw = Rect(MyMouse.sx, MyMouse.sy + i, radx, rady)
                CircleRect.normalize()
                draw.ellipse(screen, color, ellDraw, MyMouse.th)
                ellDraw = Rect(MyMouse.sx, MyMouse.sy - i, radx, rady)
                CircleRect.normalize()
                draw.ellipse(screen, color, ellDraw, MyMouse.th)
        except:
            pass #this is to stop any potential errors from stoping the program
        FindEditAreaCircle(radx, RasterGrid)
    elif tool == "rectangle":
        draw.rect(screen, color, Rect(MyMouse.sx, MyMouse.sy, MyMouse.mx - MyMouse.sx, MyMouse.my - MyMouse.sy), MyMouse.th)  # draws a rectangle using the mouse
        ##draws rectangles on the corners to make sure they look good
        draw.rect(screen, color, (MyMouse.sx - MyMouse.th / 2 + 1, MyMouse.sy - MyMouse.th / 2 + 1, MyMouse.th, MyMouse.th))
        draw.rect(screen, color, (MyMouse.mx - MyMouse.th / 2, MyMouse.sy - MyMouse.th / 2 + 1, MyMouse.th, MyMouse.th))
        draw.rect(screen, color, (MyMouse.mx - MyMouse.th / 2, MyMouse.my - MyMouse.th / 2, MyMouse.th, MyMouse.th))
        draw.rect(screen, color, (MyMouse.sx - MyMouse.th / 2 + 1, MyMouse.my - MyMouse.th / 2, MyMouse.th, MyMouse.th))
        FindEditAreaRect(RasterGrid)
    elif tool == "point":
        draw.circle(screen, color, (MyMouse.omx, MyMouse.omy), MyMouse.th) #draws a single point
        EditArea.append((MyMouse.omx, MyMouse.omy))



def getEvent():
    '''
    sets up how to get user feedback through the pygame window
    '''
    events = event.get() #events is mousebuttons, mouse buttons and scroll and other user inputs
    for evt in events: #loop through the list of potential events
        if evt.type == QUIT: #if you press on the x on the pygame window
            running = False #stop pygame loop
        if evt.type == MOUSEBUTTONDOWN and pencilUp == False: #if the mousebutton is pressed and you are drawing
            sx, sy = mouse.get_pos()  # sx and sy are used for drawing shapes and are the starting pos
            if evt.button == 4:
                MyMouse.th += 2  # scroll up to increase th (thickness)
                if MyMouse.th < 40:
                    MyMouse.th += 2  # scroll up to increase th (thickness)
                if MyMouse.pencilth < 5:
                    MyMouse.pencilth += 1
            if evt.button == 5:  # scroll down to lower th (thickness)
                if MyMouse.th > 1:  # ensure th doesnt become 0
                    MyMouse.th -= 2
                MyMouse.pencilth -= 1

def selectColour():
    print(
        "You can choose one of these colours: \nGREEN=(0, 193, 6)\nRED = (178,34,34)\nPURPLE=(226, 107, 255)\nBLUE=(0, 0, 255)\nBLACK=(0,0,0)\nWHITE=(255,255,255)\nLBLUE=(154, 219, 244)")
    correspondingValue = input(
        "write what each color stands for, seperated by commas as such: Blue, 0\n if you want to define a new colour instead type DEFINE")
    if correspondingValue.upper() == "DEFINE": #allows user to manually enter a colour
        NewColor = input("type in the RGB value and the name of the colour seperated by comma as such: (342, 45, 55)/MyColour\n this will be set as your new current color")
        rgbString, colorName = NewColor.split("/") #seperate the name from the numbers
        rgbString = rgbString.strip("( )")
        rgb = tuple(int(x) for x in rgbString.split(",")) #make a tuple
        colorName = rgb #set colorName to the rgb value
        colourList.append(colorName) #append that to the list
        color = colorName #set the color as the new color
        value = input("what numerical value do you want this color to have right now ")
    else:
        comma_index = correspondingValue.find(",") #split the user input to a value and colour
        value =  int(correspondingValue[comma_index + 1:].strip()) #assigns a value to the current colour
        possibleColor = (correspondingValue[:comma_index].strip().capitalize()) #assignes the colour
        while True:
            if possibleColor in colourList: #ensures that the color is inside the list
                color = possibleColor
                break
            else:
                print("try again! type the correct color") #loops until the correct color is entered



pencilUp = True #variable to see if the pen is on the drawing canva or not
def initialize():
    if HardCopyFail == False:
        ChooseRaster = input("do you want to open a new file or use the previous one")
        if ChooseRaster.lower() == "p":
            try:
                with open('previousRaster.txt', 'r') as file: #open file with the path
                    # Write the string to the file
                    path = file.readline()
            except FileNotFoundError:#if file not found, pass
                pass
            print(path)
        else:
            UserInputPath = input("copy and paste the raster path file")
            path = UserInputPath
        inputRaster = Raster(GetFirstRaster(path))
        if inputRaster.readOnly:
            #copyName = input("this file is read only, type in a name for the working copy we will create")
            arcpy.CreateRasterDataset_management(inputRaster.GetRasterInfo())
    user_input = input("Do you want to (d)raw or (s)elect a color? ")
    if user_input == 'd':
        tool = (input("choose tool:\n list of tools: point, pencil, eraser, brush, rectangle, circle")).lower()
        pencilUp = False
        user_input = input(
            "default colour is BLACK with the corresponding value of 0, if you want to change the colour  press s, else press enter")
        if user_input == "": #if the user presses enter
            user_input = "d"
    elif user_input == 's':
            selectColour()

def close():
    '''
    what is initiated upon the user trying to exit the program or when the color/value corresponding are being changed
    :return:
    '''
    pencilUp = True
    RasterCellIterator() #makes sure that all the edits are saved
    EditArea.clear() #clears the list to allow for a fresh start with the users next move
    closestPixel.clear()


running = True
colorChangeNum = 0 #if this is the user's first time changing colours
while running:

    initialize()
    print("Use the mouse to pick points off the screen ")
    print(EditArea)
    checkTool(screen)
    FindPixel()
    user_input = input("You can change the (t)ool, or (s)elect colour")
    if user_input.lower() == 't':
        toolChoice = (input("choose tool:\n list of tools: point, pencil, eraser, brush, rectangle, circle")).lower()
        if toolChoice in toolsList:
            tool = toolChoice
    elif user_input.lower() == 's':
        if colorChangeNum!=0:
            close()
        selectColour()
        colorChangeNum+=1
    else:
        print("Invalid input! Please try again.")
    # If the user wants to continue editing, go back to step 3. Otherwise, end the program.

    endUser = input("Do you want to continue editing? (y/n) ")
    if endUser.lower() == 'n':#if the user chooses to end
        close() #initiate closeing
        with open('previousRaster.txt', 'w') as file: #save current path to a file
            # Write the string to the file
            file.write(path)
        print("thanks!")
        running = False
    elif endUser.lower()=='y':
        user_input = 't'#keep drawing and allow them to choose a different tool




pygame_thread = threading.Thread(target=runPygame) #a thread separate flow of execution and this established the main thread which calls the previously made function
pygame_thread.start() #start the execution of the thread
pygame_thread.join()# Wait for the Pygame thread to finish before exiting
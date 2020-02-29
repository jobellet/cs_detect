# Detecting complex spikes in extracellular recording  
Deep learning-based detection of complex spikes  

You can find our preprint article on bioRxiv: https://www.biorxiv.org/content/biorxiv/early/2019/04/05/600536.full.pdf

### <a name="Tutorial">Tutorial:</a>
A tutorial explaining the workflow of the algorithm can be found here: https://colab.research.google.com/github/jobellet/detect_CS/blob/master/Tutorial_detect_cs.ipynb

The tutorial runs in colaboratory: 
https://research.google.com/colaboratory/faq.html  
This enables simple installation because it works online  
Also, we can use the GPUs that google freely provides.

### <a name="Implementations">Implementations:</a>
The software is written in python. You can use the software online using [Colaboratory](#Colaboratory) and uploading your data in your google drive or [use it on your local machine](#docker) thanks to a docker container. Both solutions are plateform independent and don't require any installation of python.

### <a name="Colaboratory">Colaboratory:</a> the platform independ and online solution
 
**1)** Intalling the software (you need to do this step only once)  
To install the software, clic on this link:   
https://colab.research.google.com/github/jobellet/detect_CS/blob/master/install_cs_detect.ipynb

This will create a folder named uneye in your google drive account where all the scripts and network weights will be stored 


**2)** Train your network  
To train a network, click on this link:  
https://colab.research.google.com/github/jobellet/detect_CS/blob/master/train_cs_detector.ipynb

This will train a network whose weights can be used later to detect complex spikes. Please look in the [tutorial](https://colab.research.google.com/github/jobellet/detect_CS/blob/master/Tutorial_detect_cs.ipynb) for an example of how to preprocess de data before training.


**3)** Detect complex spikes  
To detect complex spikes on your data, click on this link:  
https://colab.research.google.com/github/jobellet/detect_CS/blob/master/predict_cs.ipynb


### <a name="docker">Docker:</a> the platform independ and local solution

**1)** Install docker:

for [Windows](https://docs.docker.com/docker-for-windows/install/#download-docker-for-windows), [Mac](https://store.docker.com/editions/community/docker-ce-desktop-mac) or [Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/#set-up-the-repository)

You will need to create an account.


**2)** Download the docker image that contains the detect_cs software. 

run the docker app and then write in your terminal: docker pull joachimbellet/detect_cs

This will download an image containing python and all the dependencies that our algorithm requires (it might take some times).


**3)** Launch the docker container.

Docker launches a virtual machine that can only access to your local files if you instruct it to.

write in your terminal: docker run -it -p 6888:8888 -v /YourPath:/home/jovyan/work

In YourPath write the path on your machine that you want the container to access to.

!! Important: Now, don't just copy the output of the into your browser, but do the following:

Open your web browser. Enter "localhost:6688" as URL. Then you will be asked for a token. This token appeared when you entered the command above. It looks something like this: http://6688:8888/?token=775c758f58cdc82bf6ddf51a112228f4dd4229c5b3847bb1 . Copy the token (in this case 775c758f58cdc82bf6ddf51a112228f4dd4229c5b3847bb1) and log in. Now you should see the content of your folder in the web browser.

**4)** Start using detect_cs

Click on the jupyter tutorial and follow the instructions. The folder 'work' will contain the path that you entered in the previous step.

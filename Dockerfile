#base image
FROM python:3

# add script to root dir
ADD SpotifyRemix.py /

# configure timezone
ENV TZ America/Chicago

#Set Environment Vars for docker
ENV DeemixEmail = **None** \
	DeemixPass = **None** \
	DeemixHost = **None** \
	SpotID = **None** \ 
	SpotSecret = **None** \ 
	SpotRedirect = **None** \ 
	DiscordBotToken = **None** \ 
	CHANNEL = **None** 

# copy the dependencies file to the working directory
COPY requirements.txt ./

#install dependencies 
RUN pip3 --default-timeout=100 install -r requirements.txt --no-build-isolation 

# cmd to run container at start
CMD [ "python3", "./SpotifyRemix.py" ]

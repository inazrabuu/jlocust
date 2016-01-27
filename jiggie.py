from locust import HttpLocust, TaskSet, task
import json
import random

class JiggieTaskSet(TaskSet):
	#baseUrl = 'http://52.76.76.3/app/v3/'
	baseUrl = '/app/v3/'

	config = {
		'interest': 'both'
	}

	endpoints = {
		'login': 'login',
		'event_list': 'events/list/{}',
		'event_detail': 'event/details/{}/{}/{}',
		'guest_interested': 'event/interest/{}/{}/{}',
		'share': 'invitelink?',
		'social': 'partyfeed/list/{}/{}',
		'chat_list': 'conversations?',
		'setting': 'membersettings?'
	}

	def getLoginParam(self):
		return {
			"version":"1.1.0",
			"user_last_name":"Santoso",
			"about":"Mobile Tech Enthusiast , Apple Geek, & Dortmund Fans",
			"apn_token":"empty",
			"profile_image_url":"",
			"userId":"",
			"location":"jakarta, indonesia",
			"birthday":"08\/25\/1987",
			"fb_id":"321321",
			"user_first_name":"Jannes",
			"email":"chrno_7834@yahoo.com",
			"gender":"male"
		}

	def doLogin(self, param):
		endpoint = self.baseUrl + self.endpoints['login']

		return self.client.post(endpoint, param)

	def doEventList(self, fb_id, interest):
		endpoint = self.baseUrl + self.endpoints['event_list'].format(fb_id)

		return self.client.get(endpoint, name = self.endpoints['event_list'].format(':fb_id'))

	def doEventDetail(self, event_id, fb_id, interest):
		endpoint = self.baseUrl + self.endpoints['event_detail'].format(event_id, fb_id, interest)

		return self.client.get(endpoint, name = self.endpoints['event_detail'].format(':event_id', ':fb_id', ':interest'))

	def doGuestInterested(self, event_id, fb_id, interest):
		endpoint = self.baseUrl + self.endpoints['guest_interested'].format(event_id, fb_id, interest)

		return self.client.get(endpoint, name = self.endpoints['guest_interested'].format(':event_id', ':fb_id', ':interest'))

	def doSocial(self, fb_id, interest):
		endpoint = self.baseUrl + self.endpoints['social'].format(fb_id, interest)

		return self.client.get(endpoint, name = self.endpoints['social'].format(':fb_id', ':interest'))

	def doShare(self, fb_id, share_type, **kwargs):
		endpoint = self.baseUrl + self.endpoints['share']

		param = {
			'from_fb_id': fb_id
		}

		if (share_type == 'general'):
			param['type'] = 'general'
		else:
			param['type'] = 'event'
			param['event_id'] = kwargs['event_id']
			param['venue_name'] = kwargs['venue_name']

		for key in param.keys():
			endpoint += str(key) + '=' + str(param[key]) + '&'

		return self.client.get(endpoint[:-1])

	def doConversationList(self, fb_id):
		endpoint = self.baseUrl + self.endpoints['chat_list'] + 'fb_id={}'.format(fb_id)

		return self.client.get(endpoint)

	def doMemberSetting(self, fb_id):
		endpoint = self.baseUrl + self.endpoints['setting'] + 'fb_id={}'.format(fb_id)

		return self.client.get(endpoint)

	#@task(1)
	def goLogin(self):
		res = self.doLogin(self.getLoginParam())

		response = json.loads(res.content)

	#@task(1)
	def goTillEventList(self):
		res = self.doLogin(self.getLoginParam())
		login = json.loads(res.content)

		if(login['success'] == True):
			res = self.doEventList(login['data']['fb_id'], self.config['interest'])

			response = json.loads(res.content)

	#@task(1)
	def goTillEventDetail(self):
		res = self.doLogin(self.getLoginParam())
		login = json.loads(res.content)

		if (login['success'] == True):
			res = self.doEventList(login['data']['fb_id'], self.config['interest'])
			eventList = json.loads(res.content)

			if (eventList['msg'] == 'success'):
				event = random.choice(eventList['data']['events'])
				res = self.doEventDetail(event['_id'], login['data']['fb_id'], self.config['interest'])
				eventDetail = json.loads(res.content)

	@task(1)
	def goTillGuestInterested(self):
		res = self.doLogin(self.getLoginParam())
		login = json.loads(res.content)

		if (login['success'] == True):
			res = self.doEventList(login['data']['fb_id'], self.config['interest'])
			eventList = json.loads(res.content)

			if (eventList['msg'] == 'success'):
				event = random.choice(eventList['data']['events'])
				res = self.doEventDetail(event['_id'], login['data']['fb_id'], self.config['interest'])
				eventDetail = json.loads(res.content)

				res = self.doGuestInterested(event['_id'], login['data']['fb_id'], self.config['interest'])
				guestInterested = json.loads(res.content)

	@task(1)
	def goTillSocial(self):
		res = self.doLogin(self.getLoginParam())
		login = json.loads(res.content)

		if (login['success'] == True):
			res = self.doEventList(login['data']['fb_id'], self.config['interest'])
			eventList = json.loads(res.content)

			if (eventList['msg'] == 'success'):
				event = random.choice(eventList['data']['events'])
				res = self.doEventDetail(event['_id'], login['data']['fb_id'], self.config['interest'])
				
				res = self.doSocial(login['data']['fb_id'], self.config['interest'])
				print(res.content)

	#@task(1)
	def goTillShare(self):
		res = self.doLogin(self.getLoginParam())
		login = json.loads(res.content)

		if (login['success'] == True):
			res = self.doEventList(login['data']['fb_id'], self.config['interest'])
			eventList = json.loads(res.content)

			if (eventList['msg'] == 'success'):
				event = random.choice(eventList['data']['events'])
				res = self.doEventDetail(event['_id'], login['data']['fb_id'], self.config['interest'])
				eventDetail = json.loads(res.content)

				res = self.doShare(login['data']['fb_id'], 'event', event_id = event['_id'], venue_name = eventDetail['data']['events_details']['venue_name'])

	#@task(1)
	def goTillConvList(self):
		res = self.doLogin(self.getLoginParam())
		login = json.loads(res.content)

		if (login['success'] == True):
			res = self.doConversationList(login['data']['fb_id'])
			print(res.content)

	#@task(1)
	def goTillInvite(self):
		res = self.doLogin(self.getLoginParam())
		login = json.loads(res.content)

		if (login['success'] == True):
			res = self.doMemberSetting(login['data']['fb_id'])
			settings = json.loads(res.content)

			if (settings['success'] == True):
				res = self.doShare(login['data']['fb_id'], 'general')
				print(res.content)
		 

class JiggieUser(HttpLocust):
	task_set = JiggieTaskSet
	min_wait = 5000
	max_wait = 9000

from django.shortcuts import render
from django.utils import timezone
from .models import Post
from .models import Entity
from django.shortcuts import render, get_object_or_404
from .forms import PostForm
from django.shortcuts import redirect
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from django.db import connection
import wikipedia
import urllib
from urllib.request import urlopen
import json
import requests
import string
import re

def post_list(request):
	posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
	Entity.objects.all().delete()
	i = -1
	for post in posts:
		sent_tokenize_list = sent_tokenize(post.text)
		for sentence in sent_tokenize_list:
			i = i + 1
			word_list = word_tokenize(sentence)
			j = 0
			for word in word_list:
				j = j + 1
				Entity.objects.create(doc_id=i, start_pos=j, seg_text=word)
	cur = connection.cursor()
	cur.execute('DROP TABLE IF EXISTS train_dictionary, train_featuretbl, train_featureset')
	cur.execute("SELECT madlib.crf_train_fgen('train_segmenttbl', 'train_regex', 'crf_label', 'train_dictionary', 'train_featuretbl','train_featureset')")
	cur.execute('DROP TABLE IF EXISTS train_stats, train_weights')
	cur.execute("SELECT madlib.lincrf_train('train_featuretbl', 'train_featureset', 'crf_label', 'train_stats', 'train_weights', 20)")
	cur.execute('DROP TABLE IF EXISTS viterbi_m, viterbi_r')
	cur.execute("SELECT madlib.crf_test_fgen('blog_entity', 'train_dictionary', 'crf_label', 'train_regex', 'train_weights', 'viterbi_m', 'viterbi_r')")
	cur.execute('DROP TABLE IF EXISTS result')
	cur.execute("SELECT madlib.vcrf_label('blog_entity', 'viterbi_m', 'viterbi_r', 'crf_label', 'result')")
	cur.execute("SELECT seg_text from result where label='NN' OR label='NNS' OR label='NNP' OR label='NNPS'")
	mylist = cur.fetchall()
	names = []
	for item in mylist:
		item = str(item)
		item = item.strip('(",)\'\'')
		names.append(item)
	filter(None, names)
	names = [name for name in names if len(name) > 2] 
	filter("!", names)
	filter("[", names)
	filter("]", names)
	for post in posts:
		for word in post.text.split():
			temp_word = word.strip(",.")
			if temp_word in names:
				url = 'https://en.wikipedia.org/wiki/' + temp_word
				r = requests.get(url, allow_redirects=False)
				if r.status_code == 200:
					print(url)
					#my_regex = r"\b(?=\w)" + re.escape(temp_word) + r"\b(?!\w)"
					my_regex = r"\b(?=\w)" + re.escape(temp_word) + r"\b"
					#my_regex = r'\b(?=\w){0}\b'.format(temp_word)
					post.text = re.sub(my_regex, url , post.text, 1)
	

	return render(request, 'blog/post_list.html', {'posts' : posts})

def post_detail(request, pk):
	post = get_object_or_404(Post, pk=pk)
	return render(request, 'blog/post_detail.html', {'post' : post})

def post_new(request):
	if request.method == "POST":
		form = PostForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			post.published_date = timezone.now()
			post.save()
			return redirect('post_detail', pk=post.pk)
	else:
		form = PostForm()
	return render(request, 'blog/post_edit.html', {'form': form})

def post_edit(request, pk):
	post = get_object_or_404(Post, pk=pk)
	if request.method == "POST":
		form = PostForm(request.POST, instance=post)
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			post.published_date = timezone.now()
			post.save()
			return redirect('post_detail', pk=post.pk)
	else:
		form = PostForm(instance=post)
	return render(request, 'blog/post_edit.html', {'form': form})
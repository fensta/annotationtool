# assert(rel_time > 0) was violated

# [Sun May 22 16:47:33 2016] [error] data sent from client: {"relevance":"Relevant","relevance_time":null,"confidence_relevance_time":null,"confidence_relevance":"Low","fact":"Factual","fact_time":1.817,"confidence_fact_time":2.773,"confidence_fact":"Low","annotation_timestamp":"Sun, 22 May 2016 16:47:25 GMT","tweet_id":"5741b0a0f48e665ca261946c"}
# [Sun May 22 16:47:33 2016] [error] stefan\\u002eraebiger@gmail\\u002ecom has annotated 5741b0a0f48e665ca261946c - store that in DB!
# [Sun May 22 16:47:33 2016] [error] Internal Server Error: /labeler/stefan\\u002eraebiger@gmail\\u002ecom/annotation/
# [Sun May 22 16:47:33 2016] [error] Traceback (most recent call last):
# [Sun May 22 16:47:33 2016] [error]   File "/var/lib/openshift/5740ee652d52719ad3000038/python/virtenv/lib/python2.7/site-packages/django/core/handlers/base.py", line 132, in get_response
# [Sun May 22 16:47:33 2016] [error]     response = wrapped_callback(request, *callback_args, **callback_kwargs)
# [Sun May 22 16:47:33 2016] [error]   File "/var/lib/openshift/5740ee652d52719ad3000038/python/virtenv/lib/python2.7/site-packages/django/contrib/auth/decorators.py", line 22, in _wrapped_view
# [Sun May 22 16:47:33 2016] [error]     return view_func(request, *args, **kwargs)
# [Sun May 22 16:47:33 2016] [error]   File "/var/lib/openshift/5740ee652d52719ad3000038/python/virtenv/lib/python2.7/site-packages/django/utils/decorators.py", line 110, in _wrapped_view
# [Sun May 22 16:47:33 2016] [error]     response = view_func(request, *args, **kwargs)
# [Sun May 22 16:47:33 2016] [error]   File "/var/lib/openshift/5740ee652d52719ad3000038/app-root/runtime/repo/Labeller/views.py", line 122, in annotation_view
# [Sun May 22 16:47:33 2016] [error]     annotate_tweet(tweet, anno, data, fields)
# [Sun May 22 16:47:33 2016] [error]   File "/var/lib/openshift/5740ee652d52719ad3000038/app-root/runtime/repo/Labeller/util.py", line 245, in annotate_tweet
# [Sun May 22 16:47:33 2016] [error]     assert(rel_time > 0)
# [Sun May 22 16:47:33 2016] [error] AssertionError
# 91.23.97.167 - - [22/May/2016:12:47:33 -0400] "POST /labeler/stefan%5Cu002eraebiger@gmail%5Cu002ecom/annotation/ HTTP/1.1" 500 17210 "http://annotationtool-fensta.rhcloud.com/labeler/stefan%5Cu002eraebiger@gmail%5Cu002ecom/annotation/" "Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.5.0"
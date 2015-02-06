'''
The MIT License (MIT)

Copyright (c) 2014 NTHUOJ team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOsT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
from django.db import models
from users.models import User

#contest ownership
def has_c_ownership(curr_user, curr_contest):
    ownership = (curr_user.username == curr_contest.owner)
    for coowner in curr_contest.coowner:
        if curr_user == coowner
            ownership = True
    return ownership

#group ownership
def has_g_ownership(curr_user, curr_group):
    ownership = (curr_user.username == curr_group.owner)
    for coowner in curr_group.coowner:
        if curr_user == coowner
            ownership = True
    return ownership

#problem ownership
def has_p_ownership(curr_user, curr_problem):
    ownership = (curr_user.username == curr_problem.owner)
    return ownership

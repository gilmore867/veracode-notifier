# Purpose:  API utilities
#
# Notes:    API credentials must be enabled on Veracode account and placed in ~/.veracode/credentials like
#
#           [default]
#           veracode_api_key_id = <YOUR_API_KEY_ID>
#           veracode_api_key_secret = <YOUR_API_KEY_SECRET>
#
#           and file permission set appropriately (chmod 600)

import requests
import logging
from requests.adapters import HTTPAdapter

from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC
from .exceptions import VeracodeAPIError


class VeracodeAPI:
    def __init__(self, proxies=None):
        self.baseurl = "https://analysiscenter.veracode.com/api/5.0/"
        requests.Session().mount(self.baseurl, HTTPAdapter(max_retries=3))
        self.proxies = proxies

    def _get_request(self, url, params=None):
        try:
            r = requests.get(url, auth=RequestsAuthPluginVeracodeHMAC(), params=params, proxies=self.proxies)
            if 200 >= r.status_code <= 299:
                if r.content is None:
                    logging.debug("HTTP response body empty:\r\n{}\r\n{}\r\n{}\r\n\r\n{}\r\n{}\r\n{}\r\n"
                                  .format(r.request.url, r.request.headers, r.request.body, r.status_code, r.headers, r.content))
                    raise VeracodeAPIError("HTTP response body is empty")
                else:
                    return r.content
            else:
                logging.debug("HTTP error for request:\r\n{}\r\n{}\r\n{}\r\n\r\n{}\r\n{}\r\n{}\r\n"
                              .format(r.request.url, r.request.headers, r.request.body, r.status_code, r.headers, r.content))
                raise VeracodeAPIError("HTTP error: {}".format(r.status_code))
        except requests.exceptions.RequestException as e:
            logging.exception("Connection error")
            raise VeracodeAPIError(e)

    def get_app_list(self):
        """Returns all application profiles."""
        return self._get_request(self.baseurl + "getapplist.do")

    def get_app_info(self, app_id):
        """Returns application profile info for a given app ID."""
        return self._get_request(self.baseurl + "getappinfo.do", params={"app_id": app_id})

    def get_sandbox_list(self, app_id):
        """Returns a list of sandboxes for a given app ID"""
        return self._get_request(self.baseurl + "getsandboxlist.do", params={"app_id": app_id})

    def get_build_list(self, app_id, sandbox_id=None):
        """Returns all builds for a given app ID."""
        if sandbox_id is None:
            params = {"app_id": app_id}
        else:
            params = {"app_id": app_id, "sandbox_id": sandbox_id}
        return self._get_request(self.baseurl + "getbuildlist.do", params=params)
    
    def get_build_info(self, app_id, build_id, sandbox_id=None):
        """Returns build info for a given build ID."""
        if sandbox_id is None:
            params = {"app_id": app_id, "build_id": build_id}
        else:
            params = {"app_id": app_id, "build_id": build_id, "sandbox_id": sandbox_id}
        return self._get_request(self.baseurl + "getbuildinfo.do", params=params)

    def get_detailed_report(self, build_id):
        """Returns a detailed report for a given build ID."""
        return self._get_request(self.baseurl + "detailedreport.do", params={"build_id": build_id})

    def get_policy_list(self):
        """Returns all policies."""
        return self._get_request(self.baseurl + "getpolicylist.do")

    def get_user_list(self):
        """Returns all user accounts."""
        return self._get_request(self.baseurl + "getuserlist.do")

    def get_user_info(self, username):
        """Returns user info for a given username."""
        return self._get_request(self.baseurl + "getuserinfo.do", params={"username": username})
import argparse
import json
import requests


def confluence_api(url, auth_user_password):
    resp = requests.get(url, auth=auth_user_password)
    if resp.status_code == 200:
        return resp.json()['results']
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='add Sprint retro pages to Kepler')
    parser.add_argument('targetSprint', type=int,
                        help='Sprint Number')
    parser.add_argument('keplerUser', type=str, help='Kepler username')
    parser.add_argument('keplerPassword', type=str, help='Kepler password')

    args = parser.parse_args()

    base = 'http://localhost:8090'
    space_key = 'ER'

    api = '/rest/api/content'
    auth = (args.keplerUser, args.keplerPassword)

    sprintsPageId = None
    results = confluence_api(f'{base}{api}?spaceKey={space_key}&title=Sprints', auth)
    assert results is not None
    sprintsPageId = int(results[0]['id'])
    # print(sprintsPageId)
    assert sprintsPageId is not None, 'Unable to find base page for Sprints'

    # check that the target sprint does not exist
    results = confluence_api(f'{base}{api}?spaceKey={space_key}&title=Sprint {args.targetSprint}', auth)
    assert results is not None
    assert len(results) == 0, f'Error: Sprint page {args.targetSprint} already exists'

    sprintNPageId = None
    results = confluence_api(f'{base}{api}?spaceKey={space_key}&title=Sprint n', auth)
    assert results is not None
    sprintNPageId = int(results[0]['id'])
    assert sprintNPageId is not None, 'Unable to find "Sprint N" page'

    sprintNBody = None
    response = requests.get(url = f'{base}{api}/{sprintNPageId}?expand=body.storage', auth=auth)
    if response.status_code == 200:
        sprintNBody = response.json()['body']
    assert sprintNBody is not None, 'Unable to obtain body of Sprint N page'

    # create the anchor page for this sprint under 'Sprints'
    storage = {'value': sprintNBody['storage']['value'], 'representation': 'storage'}
    new_page = {'type': 'page', 'title': f'Sprint {args.targetSprint}', 'body': {'storage': storage},
                'ancestors': [{'id': sprintsPageId}],
                'space': {'key': f'{space_key}'}}
    response = requests.post(f'{base}{api}/', auth=auth, data=json.dumps(new_page), headers={'Content-Type': 'application/json'})
    assert response.status_code == 200, f'Failed to create new Sprint page with error: {response.status_code}'
    newSprintPageId = int(response.json()['id'])
    print(f'Created anchor page: Sprint {args.targetSprint} [id: {newSprintPageId}]')

    # iterate through children of 'Sprint N' & add them to the new sprint page
    results = confluence_api(f'{base}{api}/search?cql=parent={sprintNPageId}', auth)
    for r in results:
        templateId = r['id']
        response = requests.get(f'{base}{api}/{templateId}?expand=body.storage', auth=auth)
        if response.status_code == 200:
            child = response.json()
            child_title = child['title'].replace('Sprint n', f'Sprint {args.targetSprint}')
            child_storage = {'value': child['body']['storage']['value'], 'representation': 'storage'}
            new_child_page = {'type': 'page', 'title': f'{child_title}', 'body': {'storage': child_storage},
                              'ancestors': [{'id': newSprintPageId}],
                              'space': {'key': f'{space_key}'}}
            response = requests.post(f'{base}{api}/', auth=auth, data=json.dumps(new_child_page),
                                     headers={'Content-Type': 'application/json'})
            assert response.status_code == 200, f'Failed to create new Sprint Team page with error: {response.status_code}'
            print(f'Created Team Page: {child_title} [id: '+response.json()['id']+']')
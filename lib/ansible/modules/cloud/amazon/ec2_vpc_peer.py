#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'certified'}


DOCUMENTATION = '''
module: ec2_vpc_peer
short_description: create, delete, accept, and reject VPC peering connections between two VPCs.
description:
  - Read the AWS documentation for VPC Peering Connections
    U(http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/vpc-peering.html)
version_added: "2.2"
options:
  vpc_id:
    description:
      - VPC id of the requesting VPC.
    required: false
  peering_id:
    description:
      - Peering connection id.
    required: false
  peer_region:
    description:
      - Region of the accepting VPC.
    required: false
    version_added: '2.5'
  peer_vpc_id:
    description:
      - VPC id of the accepting VPC.
    required: false
  peer_owner_id:
    description:
      - The AWS account number for cross account peering.
    required: false
  tags:
    description:
      - Dictionary of tags to look for and apply when creating a Peering Connection.
    required: false
  state:
    description: The intended state of the peering connection after the run
      Setting to 'present' will create or accept ('accept' is a synonym for 'present').
      Setting to 'absent' will remove or reject ('reject' is a synonym for 'absent').
    required: false
    default: present
    choices: ['present', 'absent', 'accept', 'reject']
author: Mike Mochan(@mmochan)
extends_documentation_fragment:
    - aws
    - ec2
requirements: [ botocore, boto3, json ]
'''

EXAMPLES = '''
# Complete example to create and accept a local peering connection.
- name: Create local account VPC peering Connection
  ec2_vpc_peer:
    region: ap-southeast-2
    vpc_id: vpc-12345678
    peer_vpc_id: vpc-87654321
    state: present
    tags:
      Name: Peering connection for VPC 21 to VPC 22
      CostCode: CC1234
      Project: phoenix
  register: vpc_peer

- name: Accept local VPC peering request
  ec2_vpc_peer:
    region: ap-southeast-2
    peering_id: "{{ vpc_peer.peering_id }}"
    state: accept
  register: action_peer

# Complete example to delete a local peering connection.
- name: Create local account VPC peering Connection
  ec2_vpc_peer:
    region: ap-southeast-2
    vpc_id: vpc-12345678
    peer_vpc_id: vpc-87654321
    state: present
    tags:
      Name: Peering connection for VPC 21 to VPC 22
      CostCode: CC1234
      Project: phoenix
  register: vpc_peer

- name: delete a local VPC peering Connection
  ec2_vpc_peer:
    region: ap-southeast-2
    peering_id: "{{ vpc_peer.peering_id }}"
    state: absent
  register: vpc_peer

  # Complete example to create and accept a cross account peering connection.
- name: Create cross account VPC peering Connection
  ec2_vpc_peer:
    region: ap-southeast-2
    vpc_id: vpc-12345678
    peer_vpc_id: vpc-12345678
    peer_owner_id: 123456789102
    state: present
    tags:
      Name: Peering connection for VPC 21 to VPC 22
      CostCode: CC1234
      Project: phoenix
  register: vpc_peer

- name: Accept peering connection from remote account
  ec2_vpc_peer:
    region: ap-southeast-2
    peering_id: "{{ vpc_peer.peering_id }}"
    profile: boto3_profile_for_cross_account
    state: accept
  register: vpc_peer

# Complete example to create and accept an intra-region peering connection.
- name: Create intra-region VPC peering Connection
  ec2_vpc_peer:
    region: us-east-1
    vpc_id: vpc-12345678
    peer_vpc_id: vpc-87654321
    peer_vpc_region: us-west-2
    state: present
    tags:
      Name: Peering connection for us-east-1 VPC to us-west-2 VPC
      CostCode: CC1234
      Project: phoenix
  register: vpc_peer

- name: Accept peering connection from peer region
  ec2_vpc_peer:
    region: us-west-2
    peering_id: "{{ vpc_peer.peering_id }}"
    state: accept
  register: vpc_peer

# Complete example to create and reject a local peering connection.
- name: Create local account VPC peering Connection
  ec2_vpc_peer:
    region: ap-southeast-2
    vpc_id: vpc-12345678
    peer_vpc_id: vpc-87654321
    state: present
    tags:
      Name: Peering connection for VPC 21 to VPC 22
      CostCode: CC1234
      Project: phoenix
  register: vpc_peer

- name: Reject a local VPC peering Connection
  ec2_vpc_peer:
    region: ap-southeast-2
    peering_id: "{{ vpc_peer.peering_id }}"
    state: reject

# Complete example to create and accept a cross account peering connection.
- name: Create cross account VPC peering Connection
  ec2_vpc_peer:
    region: ap-southeast-2
    vpc_id: vpc-12345678
    peer_vpc_id: vpc-12345678
    peer_owner_id: 123456789102
    state: present
    tags:
      Name: Peering connection for VPC 21 to VPC 22
      CostCode: CC1234
      Project: phoenix
  register: vpc_peer

- name: Accept a cross account VPC peering connection request
  ec2_vpc_peer:
    region: ap-southeast-2
    peering_id: "{{ vpc_peer.peering_id }}"
    profile: bot03_profile_for_cross_account
    state: accept
    tags:
      Name: Peering connection for VPC 21 to VPC 22
      CostCode: CC1234
      Project: phoenix

# Complete example to create and reject a cross account peering connection.
- name: Create cross account VPC peering Connection
  ec2_vpc_peer:
    region: ap-southeast-2
    vpc_id: vpc-12345678
    peer_vpc_id: vpc-12345678
    peer_owner_id: 123456789102
    state: present
    tags:
      Name: Peering connection for VPC 21 to VPC 22
      CostCode: CC1234
      Project: phoenix
  register: vpc_peer

- name: Reject a cross account VPC peering Connection
  ec2_vpc_peer:
    region: ap-southeast-2
    peering_id: "{{ vpc_peer.peering_id }}"
    profile: bot03_profile_for_cross_account
    state: reject

'''
RETURN = '''
task:
  description: The result of the create, accept, reject or delete action.
  returned: success
  type: dictionary
'''

try:
    import botocore
except ImportError:
    pass  # caught by imported HAS_BOTO3

import distutils.version

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.ec2 import boto3_conn, ec2_argument_spec, get_aws_connection_info, HAS_BOTO3


def tags_changed(pcx_id, client, module):
    changed = False
    tags = dict()
    if module.params.get('tags'):
        tags = module.params.get('tags')
    pcx = find_pcx_by_id(pcx_id, client, module)
    if pcx['VpcPeeringConnections']:
        pcx_values = [t.values() for t in pcx['VpcPeeringConnections'][0]['Tags']]
        pcx_tags = [item for sublist in pcx_values for item in sublist]
        tag_values = [[key, str(value)] for key, value in tags.items()]
        tags = [item for sublist in tag_values for item in sublist]
        if sorted(pcx_tags) == sorted(tags):
            changed = False
        elif tags:
            delete_tags(pcx_id, client, module)
            create_tags(pcx_id, client, module)
            changed = True
    return changed


def describe_peering_connections(params, client):
    if 'VpcPeeringConnectionId' in params.keys():
        result = client.describe_vpc_peering_connections(
            VpcPeeringConnectionIds=[params['VpcPeeringConnectionId']]
        )
        return result

    result = client.describe_vpc_peering_connections(
        Filters=[
            {'Name': 'requester-vpc-info.vpc-id', 'Values': [params['VpcId']]},
            {'Name': 'accepter-vpc-info.vpc-id', 'Values': [params['PeerVpcId']]}
        ]
    )
    if result['VpcPeeringConnections'] == []:
        result = client.describe_vpc_peering_connections(
            Filters=[
                {'Name': 'requester-vpc-info.vpc-id', 'Values': [params['PeerVpcId']]},
                {'Name': 'accepter-vpc-info.vpc-id', 'Values': [params['VpcId']]}
            ]
        )
    return result


def is_active(peering_conn):
    return peering_conn['Status']['Code'] == 'active'


def is_pending(peering_conn):
    return peering_conn['Status']['Code'] == 'pending-acceptance'


def is_done(peering_conn):
    return peering_conn['Status']['Code'] in ['deleted', 'rejected', 'failed', 'expired']


def create_or_accept_peer_connection(client, module):
    changed = False
    params = dict()
    if module.params.get('vpc_id'):
        params['VpcId'] = module.params.get('vpc_id')
    if module.params.get('peer_vpc_id'):
        params['PeerVpcId'] = module.params.get('peer_vpc_id')
    if module.params.get('peering_id'):
        params['VpcPeeringConnectionId'] = module.params.get('peering_id')
    if module.params.get('peer_region'):
        if distutils.version.StrictVersion(botocore.__version__) < distutils.version.StrictVersion('1.8.6'):
            module.fail_json(msg="specifying peer_region parameter requires botocore >= 1.8.6")
        params['PeerRegion'] = module.params.get('peer_region')
    if module.params.get('peer_owner_id'):
        params['PeerOwnerId'] = str(module.params.get('peer_owner_id'))
    peering_conns = describe_peering_connections(params, client)
    for peering_conn in peering_conns['VpcPeeringConnections']:
        pcx_id = peering_conn['VpcPeeringConnectionId']
        if is_active(peering_conn):
            if tags_changed(pcx_id, client, module):
                changed = True
            return (changed, peering_conn['VpcPeeringConnectionId'])
        if is_pending(peering_conn):
            try:
                client.accept_vpc_peering_connection(VpcPeeringConnectionId=peering_conn['VpcPeeringConnectionId'])
                changed = True
                tags_changed(pcx_id, client, module)
                return (changed, peering_conn['VpcPeeringConnectionId'])
            except botocore.exceptions.ClientError as e:
                module.fail_json(msg=str(e))
    try:
        params.pop('VpcPeeringConnectionId', None)
        peering_conn = client.create_vpc_peering_connection(**params)
        pcx_id = peering_conn['VpcPeeringConnection']['VpcPeeringConnectionId']
        if module.params.get('tags'):
            create_tags(pcx_id, client, module)
        changed = True
        return (changed, peering_conn['VpcPeeringConnection']['VpcPeeringConnectionId'])
    except botocore.exceptions.ClientError as e:
        module.fail_json(msg=str(e))


def remove_or_reject_peer_connection(client, module):
    changed = True
    params = dict()
    if module.params.get('peering_id'):
        params['VpcPeeringConnectionId'] = module.params.get('peering_id')
    if module.params.get('vpc_id'):
        params['VpcId'] = module.params.get('vpc_id')
    if module.params.get('peer_vpc_id'):
        params['PeerVpcId'] = module.params.get('peer_vpc_id')
    if module.params.get('peer_region'):
        params['PeerRegion'] = module.params.get('peer_region')
    if module.params.get('peer_owner_id'):
        params['PeerOwnerId'] = str(module.params.get('peer_owner_id'))
    peering_conns = describe_peering_connections(params, client)
    if not peering_conns:
        module.exit_json(changed=False)
    else:
        if not peering_conns['VpcPeeringConnections']:
            module.exit_json(changed=False)
        else:
            peering_conn = peering_conns['VpcPeeringConnections'][0]
            if is_done(peering_conn):
                return(changed, peering_conn['VpcPeeringConnectionId'])
            else:
                try:
                    if is_active(peering_conn):
                        client.delete_vpc_peering_connection(VpcPeeringConnectionId=peering_conn['VpcPeeringConnectionId'])
                        changed = True
                    elif 'VpcId' in params.keys() and peering_conn['RequesterVpcInfo']['VpcId'] == params['VpcId']:
                        client.delete_vpc_peering_connection(VpcPeeringConnectionId=peering_conn['VpcPeeringConnectionId'])
                        changed = True
                    elif is_pending(peering_conn):
                        client.reject_vpc_peering_connection(VpcPeeringConnectionId=peering_conn['VpcPeeringConnectionId'])
                        changed = True
                    return(changed, peering_conn['VpcPeeringConnectionId'])
                except botocore.exceptions.ClientError as e:
                    module.fail_json(msg=str(e))


def load_tags(module):
    tags = []
    if module.params.get('tags'):
        for name, value in module.params.get('tags').items():
            tags.append({'Key': name, 'Value': str(value)})
    return tags


def create_tags(pcx_id, client, module):
    try:
        delete_tags(pcx_id, client, module)
        client.create_tags(Resources=[pcx_id], Tags=load_tags(module))
    except botocore.exceptions.ClientError as e:
        module.fail_json(msg=str(e))


def delete_tags(pcx_id, client, module):
    try:
        client.delete_tags(Resources=[pcx_id])
    except botocore.exceptions.ClientError as e:
        module.fail_json(msg=str(e))


def find_pcx_by_id(pcx_id, client, module):
    try:
        return client.describe_vpc_peering_connections(VpcPeeringConnectionIds=[pcx_id])
    except botocore.exceptions.ClientError as e:
        module.fail_json(msg=str(e))


def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            vpc_id=dict(),
            peer_vpc_id=dict(),
            peer_region=dict(),
            peering_id=dict(),
            peer_owner_id=dict(),
            tags=dict(required=False, type='dict'),
            profile=dict(),
            state=dict(default='present', choices=['present', 'absent', 'accept', 'reject'])
        )
    )
    module = AnsibleModule(argument_spec=argument_spec)

    if not HAS_BOTO3:
        module.fail_json(msg='json, botocore and boto3 are required.')
    state = module.params.get('state')
    try:
        region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
        client = boto3_conn(module, conn_type='client', resource='ec2',
                            region=region, endpoint=ec2_url, **aws_connect_kwargs)
    except botocore.exceptions.NoCredentialsError as e:
        module.fail_json(msg="Can't authorize connection - " + str(e))

    if state == 'present' or state == 'accept':
        (changed, results) = create_or_accept_peer_connection(client, module)
        module.exit_json(changed=changed, peering_id=results)
    else:
        (changed, results) = remove_or_reject_peer_connection(client, module)
        module.exit_json(changed=changed, removed_peering_id=results)


if __name__ == '__main__':
    main()

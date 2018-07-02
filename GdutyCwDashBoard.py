import os
import logging
import traceback
import boto3
import json
import re

LOG_LEVELS = {'CRITICAL' : 50, 'ERROR': 40, 'WARNING' : 30, 'INFO' : 20, 'DEBUG' : 10}

cw = boto3.client('cloudwatch')

def init_logging():
    # setting up logging for nice output of the findings
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('nose').setLevel(logging.WARNING)

    return logger

def setup_local_logging(logger):
    #Setting up logger to print to the main screen if running locally 
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger

def lambda_handler(event,context):
    try:
        global logger
        logger = init_logging()
        logger = set_log_level(logger, os.environ.get('log_level','INFO'))

        logger.debug(json.dumps(event))

        #Lets assume all GDuty CW Events have detail type
        detail_type = event['detail']['type']
        timestamp = event['time']
        #Let us publish a custom Cloudwatch Metric for GDuty findings that fall within these types:
        # Backdoor:EC2
        # CryptoCurrency:EC2
        # Becon:EC2
        # Trojan:EC2
        # UnAuthAccess:EC2
        # Behaviour:EC2
        # PenTest:IAMUser
        # Recon:IAMUser
        # Stealth:IAMUser
        # UnauthorizedAccess:IAMUser
        # Behavior:IAMUser
        # UnAuthAccess:IAMUser
        finding_type = 'unknown'
        resource = 'unknown'

        # Create named capture group that matches the finding type and resource type 
        matched = re.match('(?P<finding_type>[^:]+):(?P<resource>[^/]+)/',detail_type)
        if not matched:
            logger.debug('Unkown error match')
            exit(1)

        finding_type = matched.group(1)
        resource = matched.group(2)

        #Lets put custom metric into CW for the above finding
        cw.put_metric_data(
            Namespace = 'MyAccount',
            MetricData = [{
                'MetricName' : 'FindingsCount',
                'Dimensions' : [
                    {
                        'Name' : 'type',
                        'Value': finding_type
                    },
                    {
                        'Name':'resource',
                        'Value' : resource
                    }
                ],
                'Timestamp':timestamp,
                'Value' : 1.0,
                'Unit' : 'None',
                'StorageResolution' : 60
            }]
        )
    except SystemExit:
        logger.error("Exiting")
        sys.exit(1)
    except ValueError:
        exit(1)
    except:
        print("Unexpected error!\n Stack Trace:", traceback.format_exc())
    exit

if __name__ == "__main__":
    logger = init_logging()
    logger = setup_local_logging(logger)


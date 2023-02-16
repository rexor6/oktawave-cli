import pytest
import oktawave_cli.lib.oci
import pyodk
try:
    from unittest.mock import MagicMock, create_autospec, patch
except ImportError:
    from mock import MagicMock, create_autospec, patch

def test_get_oci_list_empty():
    with patch('oktawave_cli.lib.oci.OCIApi') as MockOCIApi:
       instance = MockOCIApi.return_value
       instance.instances_get.return_value = pyodk.ApiCollectionInstance()
       oci_helper = oktawave_cli.lib.oci.OciHelper(pyodk.ApiClient())
       result = oci_helper.get_oci_list()
       assert result is None


def test_get_oci_list_return_on_exception():
    with patch('oktawave_cli.lib.oci.OCIApi',
               side_effect=pyodk.rest.ApiException) as MockOCIApi:
       oci_helper = oktawave_cli.lib.oci.OciHelper(pyodk.ApiClient())
       result = oci_helper.get_oci_list()
       assert len(result) == 0

def test_get_oci_list():
    with patch('oktawave_cli.lib.oci.OCIApi') as MockOCIApi:
       instance1 = MagicMock()
       instance2 = MagicMock()
       instance3 = MagicMock()
       items = [instance1, instance2, instance3]
       instance = MockOCIApi.return_value
       instance.instances_get.return_value = \
       pyodk.ApiCollectionInstance(items=items)
       oci_helper = oktawave_cli.lib.oci.OciHelper(pyodk.ApiClient())
       result = oci_helper.get_oci_list()
       assert  len(result) == 3

def test_get_oci_list_return_instances_lists():
    with patch('oktawave_cli.lib.oci.OCIApi') as MockOCIApi:
       instance1 = MagicMock(spec=pyodk.models.Instance)
       instance2 = MagicMock(spec=pyodk.models.Instance)
       instance3 = MagicMock(spec=pyodk.models.Instance)
       items = [instance1, instance2, instance3]
       instance = MockOCIApi.return_value
       instance.instances_get.return_value = \
       pyodk.ApiCollectionInstance(items=items)
       oci_helper = oktawave_cli.lib.oci.OciHelper(pyodk.ApiClient())
       result = oci_helper.get_oci_list()
       assert len(result) == 3
       assert hasattr(result[0], 'id')
       assert hasattr(result[1], 'name')
       assert hasattr(result[2], 'status')

def test_oci_get_by_id_found():
    with patch('oktawave_cli.lib.oci.OCIApi') as MockOCIApi:
        oci_helper = oktawave_cli.lib.oci.OciHelper(pyodk.ApiClient())
        mock_instance = MagicMock(spec=pyodk.models.Instance)
        mock_instance.id = 1
        instance = MockOCIApi.return_value
        instance.instances_get.return_value = \
                pyodk.ApiCollectionInstance(items=[mock_instance])
        result = oci_helper.get_oci(oci_id=1)
        assert len(result) == 1
        assert result[0].id == 1

def test_oci_get_by_id_found2():
    with patch('oktawave_cli.lib.oci.OCIApi') as MockOCIApi:
        oci_helper = oktawave_cli.lib.oci.OciHelper(pyodk.ApiClient())
        mock_instance1 = MagicMock(spec=pyodk.models.Instance)
        mock_instance2 = MagicMock(spec=pyodk.models.Instance)
        mock_instance3 = MagicMock(spec=pyodk.models.Instance)
        mock_instance1.id = 1
        mock_instance2.id = 3
        mock_instance3.id = 1000

        instance = MockOCIApi.return_value
        instance.instances_get.return_value = \
                pyodk.ApiCollectionInstance(items=[mock_instance1,
                                                  mock_instance2,
                                                  mock_instance3])
        result = oci_helper.get_oci(oci_id=1)
        assert len(result) == 1
        assert result[0].id == 1

def test_oci_get_by_id_no_instances():
    """ Test results when no instances are returned """
    with patch('oktawave_cli.lib.oci.OCIApi') as MockOCIApi:
        oci_helper = oktawave_cli.lib.oci.OciHelper(pyodk.ApiClient())
        mock_instance = MagicMock(spec=pyodk.models.Instance)
        mock_instance.id = 1
        instance = MockOCIApi.return_value
        instance.instances_get.return_value = \
                pyodk.ApiCollectionInstance(items=[])
        result = oci_helper.get_oci(oci_id=1)
        assert len(result) == 0

def test_oci_get_by_id_not_found():
    """ Test results when no instances are returned """
    with patch('oktawave_cli.lib.oci.OCIApi') as MockOCIApi:
        oci_helper = oktawave_cli.lib.oci.OciHelper(pyodk.ApiClient())
        mock_instance = MagicMock(spec=pyodk.models.Instance)
        mock_instance.id = 2
        instance = MockOCIApi.return_value
        instance.instances_get.return_value = \
                pyodk.ApiCollectionInstance(items=[mock_instance])
        result = oci_helper.get_oci(oci_id=1)
        assert len(result) == 0

def test_oci_get_by_id_exception():
    """ Test results when no instances are returned """
    with patch('oktawave_cli.lib.oci.OCIApi',
               side_effect=pyodk.rest.ApiException) as MockOCIApi:
        oci_helper = oktawave_cli.lib.oci.OciHelper(pyodk.ApiClient())
        result = oci_helper.get_oci(oci_id=1)
        assert len(result) == 0

def test_oci_get_by_name_found():
    with patch('oktawave_cli.lib.oci.OCIApi') as MockOCIApi:
        oci_helper = oktawave_cli.lib.oci.OciHelper(pyodk.ApiClient())
        mock_instance = MagicMock(spec=pyodk.models.Instance)
        mock_instance.name = "foobar"
        instance = MockOCIApi.return_value
        instance.instances_get.return_value = \
                pyodk.ApiCollectionInstance(items=[mock_instance])
        result = oci_helper.get_oci(oci_name="foobar")
        assert len(result) == 1
        assert result[0].name== "foobar"

def test_oci_get_by_name_found2():
    with patch('oktawave_cli.lib.oci.OCIApi') as MockOCIApi:
        oci_helper = oktawave_cli.lib.oci.OciHelper(pyodk.ApiClient())
        mock_instance1 = MagicMock(spec=pyodk.models.Instance)
        mock_instance2 = MagicMock(spec=pyodk.models.Instance)
        mock_instance3 = MagicMock(spec=pyodk.models.Instance)
        mock_instance1.name = "foobar"
        mock_instance2.name = "foobar"
        mock_instance3.name = "foobar"

        instance = MockOCIApi.return_value
        instance.instances_get.return_value = \
                pyodk.ApiCollectionInstance(items=[mock_instance1,
                                                  mock_instance2,
                                                  mock_instance3])
        result = oci_helper.get_oci(oci_name="foobar")
        assert len(result) == 3
        assert result[0].name == "foobar"
        assert result[1].name == "foobar"
        assert result[2].name == "foobar"

def test_oci_get_by_name_not_found():
    """ Test results when no instances are returned """
    with patch('oktawave_cli.lib.oci.OCIApi') as MockOCIApi:
        oci_helper = oktawave_cli.lib.oci.OciHelper(pyodk.ApiClient())
        mock_instance = MagicMock(spec=pyodk.models.Instance)
        mock_instance.name = "foo"
        instance = MockOCIApi.return_value
        instance.instances_get.return_value = \
                pyodk.ApiCollectionInstance(items=[mock_instance])
        result = oci_helper.get_oci(oci_name="bar")
        assert len(result) == 0

def test_oci_get_by_name_exception():
    """Test result when exception is rised """
    with patch('oktawave_cli.lib.oci.OCIApi',
               side_effect=pyodk.rest.ApiException) as MockOCIApi:
        oci_helper = oktawave_cli.lib.oci.OciHelper(pyodk.ApiClient())
        result = oci_helper.get_oci(oci_name="foobar")
        assert len(result) == 0

def test_get_oci_by_id_found():
    """ Test get_oci_by_id with good result
    """
    with patch('oktawave_cli.lib.oci.OCIApi') as MockOCIApi:
        oci_helper = oktawave_cli.lib.oci.OciHelper(pyodk.ApiClient())
        mock_instance = MagicMock(spec=pyodk.models.Instance)
        mock_instance.id = 1
        mock_instance.name = "foobar"
        instance = MockOCIApi.return_value
        instance.instances_get_0.return_value = mock_instance
        result = oci_helper.get_oci_by_id(1)
        assert result.id == 1
        assert result.name == "foobar"

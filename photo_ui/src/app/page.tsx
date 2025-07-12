'use client'

import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import CameraIcon from '@mui/icons-material/Camera';
import Card from '@mui/material/Card';
import Divider from '@mui/material/Divider';
import Stack from '@mui/material/Stack';

import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import FormControl from '@mui/material/FormControl';
import { useState, useEffect } from 'react';


import Box from '@mui/material/Box';
import Tab from '@mui/material/Tab';
import TabContext from '@mui/lab/TabContext';
import TabList from '@mui/lab/TabList';
import TabPanel from '@mui/lab/TabPanel';

import AutomationPage from './automation';


export default function Home() {
  const [state, setState] = useState({
    camera: false,
    pictureProcess: false,
  });

  const [cameraOptions, setCameraOptions] = useState({
    apertureItems: [],
    isoItems: [],
    shutterItems: [],
    whiteBalanceItems: []
  });

  const [cameraSettings, setCameraSettings] = useState({
    iso: "",
    shutterspeed: "",
    aperture: "",
    whitebalance: ""
  });

  const [tabPage, setTabPage] = useState('0')

  const handleTabChange = (event: React.SyntheticEvent, newValue: string) => {
    setTabPage(newValue);
  };


  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch(`/api/status`, {
        method: "POST",
      })

      const newData = await response.json()
      if (newData.status === 'error') {
        return;
      }
      setState({ ...state, camera: newData.camera, pictureProcess: false });
      if (newData.params === undefined) {
        return;
      }
      setCameraSettings({
        iso: newData.params.iso.value,
        shutterspeed: newData.params.shutterspeed.value,
        aperture: newData.params.aperture.value,
        whitebalance: newData.params.whitebalance.value
      });
      setCameraOptions({
        apertureItems: newData.params.aperture.options,
        isoItems: newData.params.iso.options,
        shutterItems: newData.params.shutterspeed.options,
        whiteBalanceItems: newData.params.whitebalance.options
      });
    };

    fetchData();
    // here should be fixed and used properly to sync dependencies
  }, [])

  function handleCameraConnect() {
    const fetchData = async () => {
      const response = await fetch(`/api/connect`, {
        method: "POST",
      })

      const newData = await response.json()
      console.log(newData)
      if (newData.status === 'error') {
        return;
      }
      setState({
        ...state,
        camera: true,
        pictureProcess: false,
      });
      setCameraSettings({
        iso: newData.params.iso.value,
        shutterspeed: newData.params.shutterspeed.value,
        aperture: newData.params.aperture.value,
        whitebalance: newData.params.whitebalance.value
      });
      setCameraOptions({
        apertureItems: newData.params.aperture.options,
        isoItems: newData.params.iso.options,
        shutterItems: newData.params.shutterspeed.options,
        whiteBalanceItems: newData.params.whitebalance.options
      });

    };
    fetchData();
  }

  function handleCameraDisconnect() {
    const fetchData = async () => {
      const response = await fetch(`/api/disconnect`, {
        method: "POST",
      })

      const newData = await response.json()
      if (newData.status !== 'error') {
        setState({
          ...state,
          camera: false
        });
      }
    };
    fetchData();
  }

  function handleCameraPicture() {
    setState({
      ...state,
      pictureProcess: true
    });
    const fetchData = async () => {
      const response = await fetch(`/api/capture`, {
        method: "POST",
      })
      await response.json()
      setState({
        ...state,
        pictureProcess: false
      });
    };
    fetchData();
  }


  const handleChangeParam = (event: SelectChangeEvent) => {
    const fetchData = async () => {
      const response = await fetch(`/api/set_param?param_name=${event.target.name}&value=${event.target.value}`, {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
        },
        body: ""
      });

      const newData = await response.json();
      if (newData.status === 'error') {
        return;
      }
      setCameraSettings({
        ...cameraSettings,
        ...newData.param
      })
    }
    fetchData();
  };


  console.log(state)
  const isoItems = cameraOptions.isoItems.map((item: string, index: number) =>
    <MenuItem key={index} value={item}>{item}</MenuItem>
  );
  const shutterItems = cameraOptions.shutterItems.map((item: string, index: number) =>
    <MenuItem key={index} value={item}>{item}</MenuItem>
  );
  const apertureItems = cameraOptions.apertureItems.map((item: string, index: number) =>
    <MenuItem key={index} value={item}>{item}</MenuItem>
  );
  const whiteBalanceItems = cameraOptions.whiteBalanceItems.map((item: string, index: number) =>
    <MenuItem key={index} value={item}>{item}</MenuItem>
  );



  return (
    <div >
      <main >
        <TabContext value={tabPage}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <TabList onChange={handleTabChange} aria-label="tabs">
              <Tab label="Camera control" value="0" />
              <Tab label="Automation" value="1" />
            </TabList>
          </Box>
          <TabPanel value="0">
            <Card variant="outlined" sx={{ maxWidth: 600 }} >
              <Stack
                direction="column"
                justifyContent="center"
                alignItems="center"
                spacing={2}
              >
                <h1>Welcome to Camera UI</h1>
                <ButtonGroup variant="outlined" aria-label="outlined primary button group">
                  <Button onClick={handleCameraConnect}>Connect</Button>
                  <Button disabled={!state.camera} onClick={handleCameraDisconnect}>Disconnect</Button>
                  <Button disabled={!state.camera} href="/settings">Settings</Button>
                </ButtonGroup>
                <Divider />

                <Stack direction="row" spacing={1}>
                  <FormControl fullWidth>
                    <InputLabel id="iso-select-label">ISO</InputLabel>
                    <Select
                      labelId="iso-select-label"
                      id="iso-select"
                      label="ISO"
                      inputProps={{
                        name: 'iso',
                      }}
                      value={cameraSettings.iso}
                      sx={{ minWidth: 140 }}
                      onChange={handleChangeParam}
                    >
                      {isoItems}
                    </Select>

                  </FormControl>
                  <FormControl fullWidth>
                    <InputLabel id="shutter-select-label">Shutter Speed</InputLabel>
                    <Select
                      labelId="shutter-select-label"
                      id="shutter-select"
                      label="Shutter Speed"
                      inputProps={{
                        name: 'shutterspeed',
                      }}
                      value={cameraSettings.shutterspeed}
                      sx={{ minWidth: 140 }}
                      onChange={handleChangeParam}
                    >
                      {shutterItems}
                    </Select>
                  </FormControl>
                </Stack>
                <Stack direction="row" spacing={1}>
                  <FormControl fullWidth>
                    <InputLabel id="aperture-select-label">Aperture</InputLabel>
                    <Select
                      labelId="aperture-select-label"
                      id="aperture-select"
                      label="Aperture"
                      inputProps={{
                        name: 'aperture',
                      }}
                      value={cameraSettings.aperture}
                      sx={{ minWidth: 140 }}
                      onChange={handleChangeParam}
                    >
                      {apertureItems}
                    </Select>
                  </FormControl>
                  <FormControl fullWidth>
                    <InputLabel id="white-balance-select-label">White Balance</InputLabel>
                    <Select
                      labelId="white-balance-select-label"
                      id="white-balance-select"
                      label="White Balance"
                      inputProps={{
                        name: 'whitebalance',
                      }}
                      value={cameraSettings.whitebalance}
                      sx={{ minWidth: 140 }}
                      onChange={handleChangeParam}
                    >
                      {whiteBalanceItems}
                    </Select>
                  </FormControl>
                </Stack>
                <Divider />
                <ButtonGroup variant="outlined" aria-label="outlined primary button group">
                  <Button disabled={!state.camera} loading={state.pictureProcess} onClick={handleCameraPicture} loadingPosition="start" startIcon={<CameraIcon />} size="large" sx={{ fontSize: 24 }}>Picture</Button>
                </ButtonGroup>
                <Divider />
              </Stack>
            </Card>
          </TabPanel>
          <TabPanel value="1">
            <AutomationPage/>
          </TabPanel>

        </TabContext>



      </main>
      <footer className="">
      </footer>
    </div>
  );
}



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


export default function Home() {
  const [state, setState] = useState({
    camera: false,
    pictureProcess: false,
    params: { "aperture": { "options": [], "value": "" }, "iso": { "options": [], "value": "" }, "shutterspeed": { "options": [], "value": "" }, "whitebalance": { "options": [], "value": "" } }
  });

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch(`/api/status`, {
        method: "POST",
      })

      const newData = await response.json()
      setState({ ...state, ...newData })
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
      if (newData.status !== 'error') {
        setState({
          ...state,
          ...newData,
          camera: true
        });
      }
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

  const handleChangeISO = (event: SelectChangeEvent) => {
    // setAge(event.target.value as string);
    console.log(event.target.value);
    const fetchData = async () => {
      const response = await fetch(`/api/set_param?param_name=iso&value=${event.target.value}`, {
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
      setState({
        ...state,
        params: { ...state.params, "iso": newData.param.iso} 
      });
    }
    fetchData();
  };

  const handleChangeShutter = (event: SelectChangeEvent) => {
    const fetchData = async () => {
      const response = await fetch(`/api/set_param?param_name=shutterspeed&value=${event.target.value}`, {
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
      setState({
        ...state,
        params: { ...state.params, "shutterspeed": newData.param.shutterspeed }
      });
    }
    fetchData();
  };

  const handleChangeAperture = (event: SelectChangeEvent) => {
    const fetchData = async () => {
      const response = await fetch(`/api/set_param?param_name=aperture&value=${event.target.value}`, {
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
      setState({
        ...state,
        params: { ...state.params, "aperture": newData.param.aperture }
      });
    }
    fetchData();
  };

  const handleChangeWhiteBalance = (event: SelectChangeEvent) => {
    const fetchData = async () => {
      const response = await fetch(`/api/set_param?param_name=whitebalance&value=${
        event.target.value
      }`, {
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
      setState({
        ...state,
        params: { ...state.params, "whitebalance": newData.param.whitebalance }
      });
    }
    fetchData();
  };

  console.log(state)
  const isoItems = state.params.iso.options.map((item: string, index: number) =>
    <MenuItem key={index} value={item}>{item}</MenuItem>
  );
  const shutterItems = state.params.shutterspeed.options.map((item: string, index: number) =>
    <MenuItem key={index} value={item}>{item}</MenuItem>
  );
  const apertureItems = state.params.aperture.options.map((item: string, index: number) =>
    <MenuItem key={index} value={item}>{item}</MenuItem>
  );
  const whiteBalanceItems = state.params.whitebalance.options.map((item: string, index: number) =>
    <MenuItem key={index} value={item}>{item}</MenuItem>
  );



  return (
    <div >
      <main >
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
                  value={state.params.iso.value}
                  sx={{ minWidth: 140 }}
                  onChange={handleChangeISO}
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
                  value={state.params.shutterspeed.value}
                  sx={{ minWidth: 140 }}
                  onChange={handleChangeShutter}
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
                  value={state.params.aperture.value}
                  sx={{ minWidth: 140 }}
                  onChange={handleChangeAperture}
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
                  value={state.params.whitebalance.value}
                  sx={{ minWidth: 140 }}
                  onChange={handleChangeWhiteBalance}
                >
                  {whiteBalanceItems}
                </Select>
              </FormControl>
            </Stack>
            <Divider />
            <ButtonGroup variant="outlined" aria-label="outlined primary button group">
              <Button disabled={!state.camera} loading={state.pictureProcess} onClick={handleCameraPicture} loadingPosition="start" startIcon={<CameraIcon />} size="large" sx={{fontSize: 24}}>Picture</Button>
            </ButtonGroup>
            <Divider />
          </Stack>
        </Card>


      </main>
      <footer className="">
      </footer>
    </div>
  );
}



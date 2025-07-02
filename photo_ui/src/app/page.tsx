'use client'

import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import CameraIcon from '@mui/icons-material/Camera';
import { useState, useEffect } from 'react';


export default function Home() {
  const [state, setState] = useState({
    camera: false,
    pictureProcess: false
  });

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch(`/api/status`, {
        method: "POST",
      })

      const newData = await response.json()
      setState(newData)
    };

    fetchData();
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



  return (
    <div >
      <main >
        <Stack
          direction="column"
          justifyContent="center"
          alignItems="center"
          spacing={2}
        >
          <h1>Welcome to Camera UI</h1>
          <ButtonGroup variant="outlined" aria-label="outlined primary button group">
            <Button onClick={handleCameraConnect}>Connect</Button>
            <Button disabled={!state.camera} onClick={handleCameraDisconnect}>Dissconect</Button>
            <Button disabled={!state.camera} href="/settings">Settings</Button>
          </ButtonGroup>
          <ButtonGroup variant="outlined" aria-label="outlined primary button group">
            <Button disabled={!state.camera} loading={state.pictureProcess} onClick={handleCameraPicture} loadingPosition="start" startIcon={<CameraIcon />}>Picture</Button>
          </ButtonGroup>
        </Stack>

      </main>
      <footer className="">
      </footer>
    </div>
  );
}


import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import Card from '@mui/material/Card';
import Divider from '@mui/material/Divider';
import Stack from '@mui/material/Stack';
import { useState } from 'react';

enum RunState {
    Ready,
    Run
}

export default function AutomationPage() {
    const [runStatus, setRunStatus] = useState(RunState.Ready)
    const handleRun = async () => {
        setRunStatus(RunState.Ready)
        const evtSource = new EventSource("/api/run");
        evtSource.onmessage = (event: MessageEvent) => {
            console.log(event);
        }
        evtSource.onerror = (ev: Event) => {
            console.log(ev);
        }
        
    }
    const handleReset = async () => {
        await fetch(`/api/reset`, {
            method: "POST",
        })
    }

    const handleTopLightOn= async () => {
        await fetch(`/api/light?name=TOP&value=True`, {
            method: "POST",
        })
    }
    const handleTopLightOff= async () => {
        await fetch(`/api/light?name=TOP&value=False`, {
            method: "POST",
        })
    }

    return (
        <div>
            <Card variant="outlined" sx={{ maxWidth: 600 }}>
                <Stack
                    direction="column"
                    justifyContent="center"
                    alignItems="center"
                    spacing={2}
                >
                    <Divider />
                    <ButtonGroup variant="outlined" aria-label="outlined primary button group">
                        <Button onClick={handleRun} disabled={runStatus !== RunState.Ready}>Run</Button>
                        <Divider />
                        <Button onClick={handleReset}>Reset</Button>
                    </ButtonGroup>
                    <Divider />
                    <ButtonGroup variant="outlined" aria-label="outlined primary button group">
                        <Button onClick={handleTopLightOn}>Top Light ON</Button>
                        <Button onClick={handleTopLightOff}>Top Light OFF</Button>
                    </ButtonGroup>
                </Stack>

            </Card>
        </div>
    )
}
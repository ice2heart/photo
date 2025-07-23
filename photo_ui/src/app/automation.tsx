
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
        setRunStatus(RunState.Run)
        const response = await fetch(`/api/run`, {
            method: "POST",
        })
        
        setRunStatus(RunState.Ready)
        const newData = await response.json()
        if (newData.status === 'error') {
            return;
        }
        
    }
    const handleReset = async () => {
        await fetch(`/api/reset`, {
            method: "POST",
        })
    }

    const handleTopLight= async () => {
        await fetch(`/api/light?name=TOP&value=True`, {
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
                        <Button onClick={handleTopLight}>Top Light ON</Button>
                    </ButtonGroup>
                </Stack>

            </Card>
        </div>
    )
}
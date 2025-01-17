/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { MephistoApp } from "mephisto-addons";
import React from "react";
import ReactDOM from "react-dom";
import "bootstrap-chat/styles.css";
import { ChatApp, ChatMessage, DefaultTaskDescription } from "bootstrap-chat";

function RenderChatMessage({ message, mephistoContext, appContext, idx }) {
  const { agentId } = mephistoContext;
  const { currentAgentNames } = appContext.taskContext;

  return (
    <div onClick={() => alert("You clicked on message with index " + idx)}>
      <ChatMessage
        isSelf={message.id === agentId || message.id in currentAgentNames}
        agentName={
          message.id in currentAgentNames
            ? currentAgentNames[message.id]
            : message.id
        }
        message={message.text}
        taskData={message.task_data}
        messageId={message.update_id}
      />
    </div>
  );
}

function App() {
  return (
    <MephistoApp
      handleFatalError={() => null}
      hasTaskSpecificData={true}
      providerType={"inhouse"}
    >
      <ChatApp
        renderMessage={({ message, idx, mephistoContext, appContext }) => (
          <RenderChatMessage
            message={message}
            mephistoContext={mephistoContext}
            appContext={appContext}
            idx={idx}
            key={message.update_id + "-" + idx}
          />
        )}
        renderSidePane={({ mephistoContext: { taskConfig } }) => (
          <DefaultTaskDescription
            chatTitle={taskConfig.chat_title}
            taskDescriptionHtml={taskConfig.task_description}
          >
            <h2>
              This is a custom Task Description loaded from a custom bundle
            </h2>
            <p>
              It has the ability to do a number of things, like directly access
              the contents of task data, view the number of messages so far, and
              pretty much anything you make like. We're also able to control
              other components as well, as in this example we've made it so that
              if you click a message, it will alert with that message idx.
            </p>
            <p>The regular task description content will now appear below:</p>
          </DefaultTaskDescription>
        )}
      />
    </MephistoApp>
  );
}

ReactDOM.render(<App />, document.getElementById("app"));

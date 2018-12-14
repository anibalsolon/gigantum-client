import { LabbookQuery } from 'Components/labbook/LabbookQueryContainer';
import { QueryRenderer } from 'react-relay';
import environment from 'JS/createRelayEnvironment';
import React from 'react';
import renderer from 'react-test-renderer';

export default (variables, cb) => {
  renderer.create(
    <QueryRenderer
      environment={environment}
      query={LabbookQuery}
      variables={variables}
      render={({ error, props }) => {
        if (props) {
          cb(error, props);
          return <div></div>;
        } if (error) {
          console.log(error);
          return <div></div>;
        }
          return <div></div>;
      }}
    />,
  );
};
